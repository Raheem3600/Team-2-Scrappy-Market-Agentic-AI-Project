/* 07_canonical_queries.sql
   Purpose: Canonical investigation queries to validate the schema and synthetic data patterns.
   Acceptance: All queries execute successfully; results are interpretable/non-random; align with expected agent investigations.
*/

USE ScrappyMarket;
GO

/* ============================
   Q0) Sanity checks
============================ */
SELECT COUNT(*) AS SalesRows FROM dbo.Sales;

SELECT TOP 10
    SaleID, [Date], Region, StoreName, ProductName, Category, UnitsSold, SalesAmount, WasOnPromotion
FROM dbo.vw_sales_enriched
ORDER BY [Date] DESC, SalesAmount DESC;
GO

/* ============================
   Q1) Top-N products by sales in a region within a time window
   Example: "Top 5 products in Southeast last 90 days"
============================ */
DECLARE @Region1 NVARCHAR(50) = 'Southeast';
DECLARE @Start1 DATE = DATEADD(DAY, -90, (SELECT MAX([Date]) FROM dbo.Dates));
DECLARE @End1   DATE = (SELECT MAX([Date]) FROM dbo.Dates);

SELECT TOP 5
    ProductID,
    ProductName,
    Category,
    SUM(UnitsSold) AS TotalUnits,
    SUM(SalesAmount) AS TotalSales,
    SUM(MarginAmount) AS TotalMargin
FROM dbo.vw_sales_enriched
WHERE Region = @Region1
  AND [Date] BETWEEN @Start1 AND @End1
GROUP BY ProductID, ProductName, Category
ORDER BY TotalSales DESC;
GO

/* ============================
   Q2) Region performance comparison (last quarter)
   Example: "Which region performed best last quarter?"
============================ */
DECLARE @Start2 DATE = DATEADD(MONTH, -3, (SELECT MAX([Date]) FROM dbo.Dates));
DECLARE @End2   DATE = (SELECT MAX([Date]) FROM dbo.Dates);

SELECT
    Region,
    SUM(SalesAmount) AS TotalSales,
    SUM(MarginAmount) AS TotalMargin,
    CAST(SUM(MarginAmount) / NULLIF(SUM(SalesAmount), 0) AS DECIMAL(10,4)) AS MarginPct
FROM dbo.vw_sales_enriched
WHERE [Date] BETWEEN @Start2 AND @End2
GROUP BY Region
ORDER BY TotalSales DESC;
GO

/* ============================
   Q3) Promotion uplift validation (promo vs non-promo averages)
   Example: "Do promotions increase sales?"
============================ */
SELECT
    WasOnPromotion,
    COUNT(*) AS RowsCount,
    AVG(CAST(UnitsSold AS DECIMAL(10,2))) AS AvgUnits,
    AVG(SalesAmount) AS AvgSales,
    AVG(MarginAmount) AS AvgMargin
FROM dbo.vw_sales_enriched
GROUP BY WasOnPromotion
ORDER BY WasOnPromotion;
GO

/* ============================
   Q4) Most impactful promotions (sales within promo windows)
   Example: "Which promo campaign drove the most sales?"
============================ */
SELECT TOP 10
    PromotionName,
    SUM(UnitsSold) AS PromoUnits,
    SUM(SalesAmount) AS PromoSales,
    SUM(MarginAmount) AS PromoMargin
FROM dbo.vw_promo_sales_fact
WHERE PromotionName IS NOT NULL
GROUP BY PromotionName
ORDER BY PromoSales DESC;
GO

/* ============================
   Q5) Store comparison in a region (top stores)
   Example: "Top 5 stores by sales in Southeast last 60 days"
============================ */
DECLARE @Region5 NVARCHAR(50) = 'Southeast';
DECLARE @Start5 DATE = DATEADD(DAY, -60, (SELECT MAX([Date]) FROM dbo.Dates));
DECLARE @End5   DATE = (SELECT MAX([Date]) FROM dbo.Dates);

SELECT TOP 5
    StoreID,
    StoreName,
    City,
    Region,
    SUM(SalesAmount) AS TotalSales,
    SUM(UnitsSold) AS TotalUnits
FROM dbo.vw_sales_enriched
WHERE Region = @Region5
  AND [Date] BETWEEN @Start5 AND @End5
GROUP BY StoreID, StoreName, City, Region
ORDER BY TotalSales DESC;
GO

/* ============================
   Q6) Growth over time (fast-growing products)
   Compare last 30 days vs previous 30 days.
============================ */
DECLARE @End6 DATE = (SELECT MAX([Date]) FROM dbo.Dates);
DECLARE @RecentStart DATE = DATEADD(DAY, -30, @End6);
DECLARE @PriorStart  DATE = DATEADD(DAY, -60, @End6);
DECLARE @PriorEnd    DATE = DATEADD(DAY, -31, @End6);

WITH SalesByWindow AS (
    SELECT
        ProductID,
        ProductName,
        SUM(CASE WHEN [Date] BETWEEN @RecentStart AND @End6 THEN SalesAmount ELSE 0 END) AS RecentSales,
        SUM(CASE WHEN [Date] BETWEEN @PriorStart AND @PriorEnd THEN SalesAmount ELSE 0 END) AS PriorSales
    FROM dbo.vw_sales_daily_product
    GROUP BY ProductID, ProductName
)
SELECT TOP 10
    ProductID,
    ProductName,
    PriorSales,
    RecentSales,
    (RecentSales - PriorSales) AS SalesDelta,
    CAST((RecentSales - PriorSales) / NULLIF(PriorSales, 0) AS DECIMAL(10,4)) AS GrowthRate
FROM SalesByWindow
WHERE PriorSales > 0
ORDER BY GrowthRate DESC, SalesDelta DESC;
GO

/* ============================
   Q7) Trend over time (monthly sales by region)
============================ */
SELECT
    Region,
    YEAR([Date]) AS [Year],
    MONTH([Date]) AS [Month],
    SUM(SalesAmount) AS MonthlySales,
    SUM(UnitsSold) AS MonthlyUnits
FROM dbo.vw_sales_daily_store
GROUP BY Region, YEAR([Date]), MONTH([Date])
ORDER BY Region, [Year], [Month];
GO