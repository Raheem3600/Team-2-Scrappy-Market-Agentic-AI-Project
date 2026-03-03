USE ScrappyMarket;
GO

/* DEV ONLY: Clear Sales table */
DELETE FROM dbo.Sales;
GO

DECLARE @TargetRows INT = 5000;

DECLARE @Dates INT = (SELECT COUNT(*) FROM dbo.Dates);
DECLARE @Stores INT = (SELECT COUNT(*) FROM dbo.Stores);
DECLARE @Products INT = (SELECT COUNT(*) FROM dbo.Products);

DECLARE @TotalCombos INT = @Dates * @Stores * @Products;
DECLARE @KeepPct INT =
    CASE
        WHEN @TotalCombos = 0 THEN 0
        ELSE CEILING((@TargetRows * 100.0) / @TotalCombos)
    END;

-- Safety clamp (avoid keeping too little or too much)
IF @KeepPct < 5  SET @KeepPct = 5;
IF @KeepPct > 40 SET @KeepPct = 40;

PRINT CONCAT('Dates=', @Dates, ', Stores=', @Stores, ', Products=', @Products,
             ', TotalCombos=', @TotalCombos, ', KeepPct=', @KeepPct, '%');

;WITH BaseCombos AS (
    SELECT
        d.DateKey,
        d.[Date],
        d.IsWeekend,
        s.StoreID,
        s.Region,
        p.ProductID,
        p.Category,
        p.RegularPrice
    FROM dbo.Dates d
    CROSS JOIN dbo.Stores s
    CROSS JOIN dbo.Products p
),
Kept AS (
    SELECT
        bc.*,
        ABS(CHECKSUM(CONCAT(bc.DateKey,'|',bc.StoreID,'|',bc.ProductID))) % 100 AS KeepRoll
    FROM BaseCombos bc
),
WithPromo AS (
    SELECT
        k.DateKey,
        k.[Date],
        k.IsWeekend,
        k.StoreID,
        k.Region,
        k.ProductID,
        k.Category,
        k.RegularPrice,
        CASE
            WHEN EXISTS (
                SELECT 1
                FROM dbo.vw_promotions_enriched pe
                WHERE pe.ProductID = k.ProductID
                  AND k.[Date] BETWEEN pe.StartDate AND pe.EndDate
            ) THEN 1 ELSE 0
        END AS WasOnPromotion
    FROM Kept k
    WHERE k.KeepRoll < @KeepPct
),
Factors AS (
    SELECT
        wp.*,

        /* Region differences */
        CASE wp.Region
            WHEN 'Southeast' THEN 1.20
            WHEN 'South'     THEN 1.10
            WHEN 'Southwest' THEN 1.00
            WHEN 'Mountain'  THEN 0.90
            ELSE 1.00
        END AS RegionFactor,

        /* Category baseline */
        CASE wp.Category
            WHEN 'Produce'  THEN 1.15
            WHEN 'Dairy'    THEN 1.05
            WHEN 'Bakery'   THEN 1.00
            WHEN 'Pantry'   THEN 0.95
            WHEN 'Frozen'   THEN 0.90
            WHEN 'Meat'     THEN 0.85
            WHEN 'Seafood'  THEN 0.70
            ELSE 0.95
        END AS CategoryFactor,

        /* Top-selling products */
        CASE WHEN wp.ProductID IN (101, 201, 301, 601) THEN 1.35 ELSE 1.00 END AS TopSellerFactor,

        /* Fast-growing product (603) */
        CASE WHEN wp.ProductID = 603 THEN 1 ELSE 0 END AS IsGrowthProduct,

        /* Weekend boost (use Dates.IsWeekend for reliability) */
        CASE WHEN wp.IsWeekend = 1 THEN 1.10 ELSE 1.00 END AS WeekendFactor

    FROM WithPromo wp
),
Computed AS (
    SELECT
        f.DateKey,
        f.StoreID,
        f.ProductID,
        f.RegularPrice,
        f.WasOnPromotion,

        /* Growth over time (only for 603) */
        CASE
            WHEN f.IsGrowthProduct = 1 THEN
                1.00 + (DATEDIFF(DAY, (SELECT MIN([Date]) FROM dbo.Dates), f.[Date]) * 0.003)
            ELSE 1.00
        END AS GrowthFactor,

        f.RegionFactor,
        f.CategoryFactor,
        f.TopSellerFactor,
        f.WeekendFactor,

        /* Deterministic jitter (approx 0.85 to 1.15) */
        (0.85 + (ABS(CHECKSUM(CONCAT('J|',f.DateKey,'|',f.StoreID,'|',f.ProductID))) % 31) / 100.0) AS Jitter

    FROM Factors f
),
FinalMeasures AS (
    SELECT
        c.DateKey,
        c.StoreID,
        c.ProductID,
        c.WasOnPromotion,

        /* UnitsSold (ensure >= 1 to avoid "empty" facts) */
        CASE
            WHEN CAST(ROUND(
                (
                    CASE
                        WHEN c.CategoryFactor >= 1.10 THEN 10
                        WHEN c.CategoryFactor >= 1.00 THEN 7
                        WHEN c.CategoryFactor >= 0.90 THEN 5
                        ELSE 3
                    END
                    * c.RegionFactor * c.CategoryFactor * c.TopSellerFactor
                    * c.WeekendFactor * c.GrowthFactor
                    * (CASE WHEN c.WasOnPromotion = 1 THEN 1.25 ELSE 1.00 END)
                    * c.Jitter
                ), 0) AS INT) < 1
            THEN 1
            ELSE CAST(ROUND(
                (
                    CASE
                        WHEN c.CategoryFactor >= 1.10 THEN 10
                        WHEN c.CategoryFactor >= 1.00 THEN 7
                        WHEN c.CategoryFactor >= 0.90 THEN 5
                        ELSE 3
                    END
                    * c.RegionFactor * c.CategoryFactor * c.TopSellerFactor
                    * c.WeekendFactor * c.GrowthFactor
                    * (CASE WHEN c.WasOnPromotion = 1 THEN 1.25 ELSE 1.00 END)
                    * c.Jitter
                ), 0) AS INT)
        END AS UnitsSold,

        /* Discount effect on price during promotion */
        (c.RegularPrice * (CASE WHEN c.WasOnPromotion = 1 THEN 0.90 ELSE 1.00 END)) AS EffectivePrice

    FROM Computed c
)
INSERT INTO dbo.Sales
(
    DateKey, StoreID, ProductID,
    UnitsSold, SalesAmount, CostAmount, MarginAmount,
    WasOnPromotion
)
SELECT
    fm.DateKey,
    fm.StoreID,
    fm.ProductID,
    fm.UnitsSold,

    CAST(ROUND(fm.UnitsSold * fm.EffectivePrice, 2) AS DECIMAL(10,2)) AS SalesAmount,

    CAST(ROUND(
        (fm.UnitsSold * fm.EffectivePrice) *
        (0.65 + (ABS(CHECKSUM(CONCAT('C|',fm.DateKey,'|',fm.StoreID,'|',fm.ProductID))) % 14) / 100.0),
        2
    ) AS DECIMAL(10,2)) AS CostAmount,

    CAST(0.00 AS DECIMAL(10,2)) AS MarginAmount,  -- set next
    CAST(fm.WasOnPromotion AS BIT) AS WasOnPromotion
FROM FinalMeasures fm;
GO

/* MarginAmount = SalesAmount - CostAmount */
UPDATE s
SET s.MarginAmount = CAST(ROUND(s.SalesAmount - s.CostAmount, 2) AS DECIMAL(10,2))
FROM dbo.Sales s;
GO

/* Verify */
SELECT COUNT(*) AS SalesRows FROM dbo.Sales;

SELECT WasOnPromotion, AVG(UnitsSold) AS AvgUnits, AVG(SalesAmount) AS AvgSales
FROM dbo.Sales
GROUP BY WasOnPromotion;
GO