/* 03_views.sql */
USE ScrappyMarket;
GO

CREATE OR ALTER VIEW dbo.vw_sales_daily_store AS
SELECT
    s.DateKey,
    d.[Date],
    s.StoreID,
    st.Region,
    st.City,
    SUM(s.UnitsSold) AS UnitsSold,
    SUM(s.SalesAmount) AS SalesAmount,
    SUM(s.CostAmount) AS CostAmount,
    SUM(s.MarginAmount) AS MarginAmount
FROM dbo.Sales s
JOIN dbo.Dates d   ON d.DateKey = s.DateKey
JOIN dbo.Stores st ON st.StoreID = s.StoreID
GROUP BY s.DateKey, d.[Date], s.StoreID, st.Region, st.City;
GO

CREATE OR ALTER VIEW dbo.vw_low_stock AS
SELECT
    i.DateKey,
    d.[Date],
    i.StoreID,
    st.Region,
    i.ProductID,
    p.ProductName,
    i.OnHandQuantity,
    i.ReorderPoint,
    CASE WHEN i.OnHandQuantity <= i.ReorderPoint THEN 1 ELSE 0 END AS IsBelowReorderPoint
FROM dbo.Inventory i
JOIN dbo.Dates d   ON d.DateKey = i.DateKey
JOIN dbo.Stores st ON st.StoreID = i.StoreID
JOIN dbo.Products p ON p.ProductID = i.ProductID;
GO

CREATE OR ALTER VIEW dbo.vw_sales_enriched AS
SELECT
    s.SaleID,
    s.DateKey,
    d.[Date],
    d.DayOfWeek,
    d.DayName,
    d.[Month],
    d.MonthName,
    d.Quarter,
    d.[Year],
    d.WeekOfYear,
    d.IsWeekend,

    s.StoreID,
    st.StoreName,
    st.City,
    st.Region,
    st.StoreType,

    s.ProductID,
    p.ProductName,
    p.Category,
    p.SubCategory,
    p.Brand,
    p.RegularPrice,

    s.UnitsSold,
    s.SalesAmount,
    s.CostAmount,
    s.MarginAmount,
    s.WasOnPromotion
FROM dbo.Sales s
JOIN dbo.Dates d   ON d.DateKey = s.DateKey
JOIN dbo.Stores st ON st.StoreID = s.StoreID
JOIN dbo.Products p ON p.ProductID = s.ProductID;
GO

CREATE OR ALTER VIEW dbo.vw_promotions_enriched AS
SELECT
    pr.PromotionID,
    pr.PromotionName,
    pr.StartDateKey,
    dStart.[Date] AS StartDate,
    pr.EndDateKey,
    dEnd.[Date]   AS EndDate,
    pr.DiscountType,
    pr.DiscountValue,
    pp.ProductID
FROM dbo.Promotions pr
JOIN dbo.Dates dStart ON dStart.DateKey = pr.StartDateKey
JOIN dbo.Dates dEnd   ON dEnd.DateKey   = pr.EndDateKey
JOIN dbo.PromotionProducts pp ON pp.PromotionID = pr.PromotionID;
GO

CREATE OR ALTER VIEW dbo.vw_sales_daily_product AS
SELECT
    s.DateKey,
    d.[Date],
    d.[Month],
    d.MonthName,
    d.Quarter,
    d.[Year],

    s.ProductID,
    p.ProductName,
    p.Category,
    p.SubCategory,
    p.Brand,

    SUM(s.UnitsSold) AS UnitsSold,
    SUM(s.SalesAmount) AS SalesAmount,
    SUM(s.CostAmount) AS CostAmount,
    SUM(s.MarginAmount) AS MarginAmount,

    MAX(CASE WHEN s.WasOnPromotion = 1 THEN 1 ELSE 0 END) AS WasOnPromotion
FROM dbo.Sales s
JOIN dbo.Dates d    ON d.DateKey = s.DateKey
JOIN dbo.Products p ON p.ProductID = s.ProductID
GROUP BY
    s.DateKey, d.[Date], d.[Month], d.MonthName, d.Quarter, d.[Year],
    s.ProductID, p.ProductName, p.Category, p.SubCategory, p.Brand;
GO

CREATE OR ALTER VIEW dbo.vw_promo_sales_fact AS
SELECT
    ve.SaleID,
    ve.[Date],
    ve.DateKey,
    ve.[Month],
    ve.Quarter,
    ve.[Year],
    ve.StoreID,
    ve.Region,
    ve.ProductID,
    ve.ProductName,
    ve.Category,
    ve.UnitsSold,
    ve.SalesAmount,
    ve.MarginAmount,
    ve.WasOnPromotion,

    pe.PromotionID,
    pe.PromotionName,
    pe.StartDate,
    pe.EndDate,
    pe.DiscountType,
    pe.DiscountValue
FROM dbo.vw_sales_enriched ve
LEFT JOIN dbo.vw_promotions_enriched pe
    ON pe.ProductID = ve.ProductID
   AND ve.[Date] BETWEEN pe.StartDate AND pe.EndDate;
GO