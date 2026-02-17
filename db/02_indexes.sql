/* 02_indexes.sql */
USE ScrappyMarket;
GO

-- Sales: common filters/grouping: DateKey, StoreID, ProductID
CREATE INDEX IX_Sales_DateKey ON dbo.Sales(DateKey);
CREATE INDEX IX_Sales_StoreID_DateKey ON dbo.Sales(StoreID, DateKey);
CREATE INDEX IX_Sales_ProductID_DateKey ON dbo.Sales(ProductID, DateKey);
CREATE INDEX IX_Sales_WasOnPromotion_DateKey ON dbo.Sales(WasOnPromotion, DateKey);

-- Inventory: common lookup is (StoreID, ProductID) latest snapshot by DateKey
CREATE INDEX IX_Inventory_Store_Product_Date ON dbo.Inventory(StoreID, ProductID, DateKey);

-- Promotions: date range filtering
CREATE INDEX IX_Promotions_Start_End ON dbo.Promotions(StartDateKey, EndDateKey);

-- Bridge table is already indexed via composite PK; add Product lookup for reverse joins
CREATE INDEX IX_PromotionProducts_ProductID ON dbo.PromotionProducts(ProductID);
GO