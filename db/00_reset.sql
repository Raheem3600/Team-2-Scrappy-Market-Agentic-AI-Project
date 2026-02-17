USE ScrappyMarket;
GO

IF OBJECT_ID('dbo.Users', 'U') IS NOT NULL DROP TABLE dbo.Users;
IF OBJECT_ID('dbo.Inventory', 'U') IS NOT NULL DROP TABLE dbo.Inventory;
IF OBJECT_ID('dbo.Sales', 'U') IS NOT NULL DROP TABLE dbo.Sales;
IF OBJECT_ID('dbo.PromotionProducts', 'U') IS NOT NULL DROP TABLE dbo.PromotionProducts;
IF OBJECT_ID('dbo.Promotions', 'U') IS NOT NULL DROP TABLE dbo.Promotions;
IF OBJECT_ID('dbo.Products', 'U') IS NOT NULL DROP TABLE dbo.Products;
IF OBJECT_ID('dbo.Stores', 'U') IS NOT NULL DROP TABLE dbo.Stores;
IF OBJECT_ID('dbo.Dates', 'U') IS NOT NULL DROP TABLE dbo.Dates;
GO