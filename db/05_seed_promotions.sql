USE ScrappyMarket;
GO

/* =========================================
   Clean existing (DEV ONLY)
========================================= */
DELETE FROM dbo.PromotionProducts;
DELETE FROM dbo.Promotions;
GO

DECLARE @P1 INT, @P2 INT, @P3 INT, @P4 INT, @P5 INT;

/* =========================================
   Promotion 1 – Back-to-School (Produce + Bakery)
========================================= */
INSERT INTO dbo.Promotions (PromotionName, StartDateKey, EndDateKey, DiscountType, DiscountValue)
VALUES (
    'Back-to-School Savings',
    (SELECT DateKey FROM dbo.Dates WHERE [Date] = '2025-09-05'),
    (SELECT DateKey FROM dbo.Dates WHERE [Date] = '2025-09-12'),
    'PERCENT',
    15.00
);
SET @P1 = SCOPE_IDENTITY();


/* =========================================
   Promotion 2 – Fall Pantry Deal
========================================= */
INSERT INTO dbo.Promotions (PromotionName, StartDateKey, EndDateKey, DiscountType, DiscountValue)
VALUES (
    'Fall Pantry Deal',
    (SELECT DateKey FROM dbo.Dates WHERE [Date] = '2025-10-20'),
    (SELECT DateKey FROM dbo.Dates WHERE [Date] = '2025-10-27'),
    'FIXED',
    1.00
);
SET @P2 = SCOPE_IDENTITY();


/* =========================================
   Promotion 3 – Thanksgiving Week
========================================= */
INSERT INTO dbo.Promotions (PromotionName, StartDateKey, EndDateKey, DiscountType, DiscountValue)
VALUES (
    'Thanksgiving Week Promo',
    (SELECT DateKey FROM dbo.Dates WHERE [Date] = '2025-11-24'),
    (SELECT DateKey FROM dbo.Dates WHERE [Date] = '2025-11-30'),
    'PERCENT',
    20.00
);
SET @P3 = SCOPE_IDENTITY();


/* =========================================
   Promotion 4 – Holiday Frozen Specials
========================================= */
INSERT INTO dbo.Promotions (PromotionName, StartDateKey, EndDateKey, DiscountType, DiscountValue)
VALUES (
    'Holiday Frozen Specials',
    (SELECT DateKey FROM dbo.Dates WHERE [Date] = '2025-12-15'),
    (SELECT DateKey FROM dbo.Dates WHERE [Date] = '2025-12-22'),
    'PERCENT',
    12.00
);
SET @P4 = SCOPE_IDENTITY();


/* =========================================
   Promotion 5 – New Year Essentials
========================================= */
INSERT INTO dbo.Promotions (PromotionName, StartDateKey, EndDateKey, DiscountType, DiscountValue)
VALUES (
    'New Year Essentials',
    (SELECT DateKey FROM dbo.Dates WHERE [Date] = '2026-01-10'),
    (SELECT DateKey FROM dbo.Dates WHERE [Date] = '2026-01-17'),
    'FIXED',
    0.75
);
SET @P5 = SCOPE_IDENTITY();


/* =========================================
   Product Mapping
========================================= */

-- P1: Produce + Bakery
INSERT INTO dbo.PromotionProducts (PromotionID, ProductID)
VALUES
(@P1, 101), (@P1, 102), (@P1, 301), (@P1, 303);

-- P2: Pantry
INSERT INTO dbo.PromotionProducts (PromotionID, ProductID)
VALUES
(@P2, 601), (@P2, 602), (@P2, 603);

-- P3: Meat + Dairy
INSERT INTO dbo.PromotionProducts (PromotionID, ProductID)
VALUES
(@P3, 401), (@P3, 402), (@P3, 204);

-- P4: Frozen
INSERT INTO dbo.PromotionProducts (PromotionID, ProductID)
VALUES
(@P4, 501), (@P4, 502);

-- P5: Dairy + Pantry
INSERT INTO dbo.PromotionProducts (PromotionID, ProductID)
VALUES
(@P5, 201), (@P5, 203), (@P5, 603);

GO