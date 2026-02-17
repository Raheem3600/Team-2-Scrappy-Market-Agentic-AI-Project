/* 01_schema.sql */
USE ScrappyMarket;
GO

/* 1) Dates */
CREATE TABLE dbo.Dates (
    DateKey     INT          NOT NULL PRIMARY KEY,  -- YYYYMMDD
    [Date]      DATE         NOT NULL,
    DayOfWeek   TINYINT      NOT NULL,              -- 1-7
    DayName     NVARCHAR(20) NOT NULL,
    [Month]     TINYINT      NOT NULL,              -- 1-12
    MonthName   NVARCHAR(20) NOT NULL,
    Quarter     TINYINT      NOT NULL,              -- 1-4
    [Year]      INT          NOT NULL,
    WeekOfYear  TINYINT      NOT NULL,
    IsWeekend   BIT          NOT NULL
);
GO

/* 2) Stores */
CREATE TABLE dbo.Stores (
    StoreID     INT           NOT NULL PRIMARY KEY,
    StoreName   NVARCHAR(100) NOT NULL,
    City        NVARCHAR(100) NOT NULL,
    Region      NVARCHAR(50)  NOT NULL,
    StoreType   NVARCHAR(50)  NULL
);
GO

/* 3) Products */
CREATE TABLE dbo.Products (
    ProductID     INT           NOT NULL PRIMARY KEY,
    ProductName   NVARCHAR(150) NOT NULL,
    Category      NVARCHAR(50)  NOT NULL,
    SubCategory   NVARCHAR(50)  NULL,
    Brand         NVARCHAR(50)  NULL,
    RegularPrice  DECIMAL(10,2) NOT NULL
);
GO

/* 4) Promotions */
CREATE TABLE dbo.Promotions (
    PromotionID    INT           NOT NULL IDENTITY(1,1) PRIMARY KEY,
    PromotionName  NVARCHAR(100) NOT NULL,
    StartDateKey   INT           NOT NULL,
    EndDateKey     INT           NOT NULL,
    DiscountType   NVARCHAR(20)  NOT NULL,       -- PERCENT / FIXED
    DiscountValue  DECIMAL(10,2) NOT NULL,

    CONSTRAINT FK_Promotions_StartDateKey FOREIGN KEY (StartDateKey)
        REFERENCES dbo.Dates(DateKey),
    CONSTRAINT FK_Promotions_EndDateKey FOREIGN KEY (EndDateKey)
        REFERENCES dbo.Dates(DateKey),

    CONSTRAINT CK_Promotions_DateRange CHECK (StartDateKey <= EndDateKey),
    CONSTRAINT CK_Promotions_DiscountType CHECK (DiscountType IN ('PERCENT','FIXED'))
);
GO

/* 5) PromotionProducts (bridge) */
CREATE TABLE dbo.PromotionProducts (
    PromotionID INT NOT NULL,
    ProductID   INT NOT NULL,

    CONSTRAINT PK_PromotionProducts PRIMARY KEY (PromotionID, ProductID),

    CONSTRAINT FK_PromotionProducts_PromotionID FOREIGN KEY (PromotionID)
        REFERENCES dbo.Promotions(PromotionID),

    CONSTRAINT FK_PromotionProducts_ProductID FOREIGN KEY (ProductID)
        REFERENCES dbo.Products(ProductID)
);
GO

/* 6) Sales */
CREATE TABLE dbo.Sales (
    SaleID         INT           NOT NULL IDENTITY(1,1) PRIMARY KEY,
    DateKey        INT           NOT NULL,
    StoreID        INT           NOT NULL,
    ProductID      INT           NOT NULL,

    UnitsSold      INT           NOT NULL,
    SalesAmount    DECIMAL(10,2) NOT NULL,
    CostAmount     DECIMAL(10,2) NOT NULL,
    MarginAmount   DECIMAL(10,2) NOT NULL,
    WasOnPromotion BIT           NOT NULL,

    CONSTRAINT FK_Sales_DateKey FOREIGN KEY (DateKey)
        REFERENCES dbo.Dates(DateKey),
    CONSTRAINT FK_Sales_StoreID FOREIGN KEY (StoreID)
        REFERENCES dbo.Stores(StoreID),
    CONSTRAINT FK_Sales_ProductID FOREIGN KEY (ProductID)
        REFERENCES dbo.Products(ProductID),

    CONSTRAINT CK_Sales_UnitsSold CHECK (UnitsSold >= 0),
    CONSTRAINT CK_Sales_Amounts CHECK (SalesAmount >= 0 AND CostAmount >= 0)
);
GO

/* 7) Inventory */
CREATE TABLE dbo.Inventory (
    InventoryID     INT NOT NULL IDENTITY(1,1) PRIMARY KEY,
    DateKey         INT NOT NULL,
    StoreID         INT NOT NULL,
    ProductID       INT NOT NULL,

    OnHandQuantity  INT NOT NULL,
    ReorderPoint    INT NOT NULL,

    CONSTRAINT FK_Inventory_DateKey FOREIGN KEY (DateKey)
        REFERENCES dbo.Dates(DateKey),
    CONSTRAINT FK_Inventory_StoreID FOREIGN KEY (StoreID)
        REFERENCES dbo.Stores(StoreID),
    CONSTRAINT FK_Inventory_ProductID FOREIGN KEY (ProductID)
        REFERENCES dbo.Products(ProductID),

    CONSTRAINT CK_Inventory_Qty CHECK (OnHandQuantity >= 0 AND ReorderPoint >= 0)
);
GO

/* 8) Users */
CREATE TABLE dbo.Users (
    UserID       INT           NOT NULL IDENTITY(1,1) PRIMARY KEY,
    Username     NVARCHAR(100) NOT NULL,
    Email        NVARCHAR(150) NOT NULL,
    PasswordHash NVARCHAR(255) NOT NULL,
    Role         NVARCHAR(50)  NOT NULL,
    CreatedAt    DATETIME      NOT NULL,
    IsActive     BIT           NOT NULL,

    CONSTRAINT UQ_Users_Username UNIQUE (Username),
    CONSTRAINT UQ_Users_Email UNIQUE (Email)
);
GO