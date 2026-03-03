
--Quick sanity checks 
--Products mapped per promotion
SELECT
  pr.PromotionName,
  COUNT(*) AS MappedProducts
FROM dbo.PromotionProducts pp
JOIN dbo.Promotions pr ON pr.PromotionID = pp.PromotionID
GROUP BY pr.PromotionName
ORDER BY pr.PromotionName;
--Ensure no duplicate mappings (same promo + product twice)
SELECT
  PromotionID,
  ProductID,
  COUNT(*) AS DupCount
FROM dbo.PromotionProducts
GROUP BY PromotionID, ProductID
HAVING COUNT(*) > 1;

--Validate promotion windows
SELECT *
FROM dbo.Promotions
WHERE StartDateKey > EndDateKey;

--Identify products under promotion (acceptance query)
SELECT
  pe.PromotionName,
  pe.StartDate,
  pe.EndDate,
  p.ProductID,
  p.ProductName,
  p.Category
FROM dbo.vw_promotions_enriched pe
JOIN dbo.Products p ON p.ProductID = pe.ProductID
ORDER BY pe.PromotionName, p.Category, p.ProductName;

--Row Count--

SELECT COUNT(*) AS SalesRows FROM dbo.Sales;
--Promotion Uplift Validation--

SELECT
    WasOnPromotion,
    AVG(UnitsSold) AS AvgUnits,
    AVG(SalesAmount) AS AvgSales
FROM dbo.Sales
GROUP BY WasOnPromotion;

--Confirm Fast-Growing Product (603)--

SELECT
    ProductID,
    MIN([Date]) AS StartDate,
    MAX([Date]) AS EndDate,
    SUM(CASE WHEN [Date] < '2025-12-01' THEN SalesAmount ELSE 0 END) AS EarlySales,
    SUM(CASE WHEN [Date] >= '2025-12-01' THEN SalesAmount ELSE 0 END) AS LateSales
FROM dbo.vw_sales_enriched
WHERE ProductID = 603
GROUP BY ProductID;

--Proper Growth Validation--

SELECT
    AVG(CASE WHEN [Date] < '2025-12-01' THEN SalesAmount END) AS AvgEarly,
    AVG(CASE WHEN [Date] >= '2025-12-01' THEN SalesAmount END) AS AvgLate
FROM dbo.vw_sales_enriched
WHERE ProductID = 603;

