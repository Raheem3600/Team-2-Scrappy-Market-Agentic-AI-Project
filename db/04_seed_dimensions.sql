USE ScrappyMarket;
GO

/* =========================================
   Safety: Clear existing dimension data
   (Run only in dev)
========================================= */
DELETE FROM dbo.Dates;
DELETE FROM dbo.Products;
DELETE FROM dbo.Stores;
GO

/* =========================================
   1) STORES (8 stores, multiple regions)
========================================= */
INSERT INTO dbo.Stores (StoreID, StoreName, City, Region, StoreType)
VALUES
(1, 'Scrappy Market - Midtown',   'Atlanta',        'Southeast', 'Urban'),
(2, 'Scrappy Market - Buckhead',  'Atlanta',        'Southeast', 'Urban'),
(3, 'Scrappy Market - Alpharetta','Alpharetta',     'Southeast', 'Suburban'),
(4, 'Scrappy Market - Marietta',  'Marietta',       'Southeast', 'Suburban'),
(5, 'Scrappy Market - Austin',    'Austin',         'South',     'Urban'),
(6, 'Scrappy Market - Dallas',    'Dallas',         'South',     'Suburban'),
(7, 'Scrappy Market - Denver',    'Denver',         'Mountain',  'Urban'),
(8, 'Scrappy Market - Phoenix',   'Phoenix',        'Southwest', 'Suburban');
GO

/* =========================================
   2) PRODUCTS (24 products, grocery categories)
========================================= */
INSERT INTO dbo.Products (ProductID, ProductName, Category, SubCategory, Brand, RegularPrice)
VALUES
-- Produce
(101, 'Bananas (1 lb)',                 'Produce', 'Fruit',      'Scrappy Fresh', 0.59),
(102, 'Gala Apples (1 lb)',             'Produce', 'Fruit',      'Scrappy Fresh', 1.49),
(103, 'Strawberries (1 lb)',            'Produce', 'Fruit',      'Scrappy Fresh', 3.99),
(104, 'Romaine Lettuce',                'Produce', 'Vegetable',  'Scrappy Fresh', 2.49),
(105, 'Tomatoes (1 lb)',                'Produce', 'Vegetable',  'Scrappy Fresh', 1.99),

-- Dairy
(201, 'Whole Milk (1 gal)',             'Dairy',   'Milk',       'DairyPure',     3.79),
(202, 'Greek Yogurt (32 oz)',           'Dairy',   'Yogurt',     'Chobani',       5.49),
(203, 'Cheddar Cheese (8 oz)',          'Dairy',   'Cheese',     'Tillamook',     4.99),
(204, 'Butter (16 oz)',                 'Dairy',   'Butter',     'Land O Lakes',  4.59),

-- Bakery
(301, 'Sandwich Bread (20 oz)',         'Bakery',  'Bread',      'Wonder',        2.79),
(302, 'Bagels (6 ct)',                  'Bakery',  'Bagels',     'Thomas',        3.49),
(303, 'Tortillas (10 ct)',              'Bakery',  'Wraps',      'Mission',       2.99),

-- Meat/Seafood
(401, 'Chicken Breast (1 lb)',          'Meat',    'Poultry',    'Scrappy Farms', 5.99),
(402, 'Ground Beef 80/20 (1 lb)',       'Meat',    'Beef',       'Scrappy Farms', 6.49),
(403, 'Salmon Fillet (1 lb)',           'Seafood', 'Fish',       'SeaBest',       11.99),

-- Frozen
(501, 'Frozen Pizza',                   'Frozen',  'Entrees',    'DiGiorno',      7.99),
(502, 'Frozen Mixed Vegetables (16 oz)','Frozen',  'Vegetables', 'Birds Eye',     2.49),

-- Pantry
(601, 'Pasta (1 lb)',                   'Pantry',  'Pasta',      'Barilla',       1.99),
(602, 'Rice (5 lb)',                    'Pantry',  'Rice',       'Mahatma',       6.99),
(603, 'Olive Oil (16.9 oz)',            'Pantry',  'Oil',        'Bertolli',      9.49),
(604, 'Cereal (18 oz)',                 'Pantry',  'Breakfast',  'Cheerios',      4.99),
(605, 'Peanut Butter (16 oz)',          'Pantry',  'Spreads',    'Jif',           3.99),

-- Beverages
(701, 'Coffee (12 oz)',                 'Beverages','Coffee',    'Starbucks',     9.99),
(702, 'Orange Juice (59 oz)',           'Beverages','Juice',     'Tropicana',     4.29),
(703, 'Sparkling Water (12 pk)',        'Beverages','Water',     'LaCroix',       5.99);
GO

/* =========================================
   3) DATES (6 months daily records)
   DateKey format: YYYYMMDD
========================================= */
DECLARE @StartDate DATE = '2025-08-01';
DECLARE @EndDate   DATE = '2026-01-31';

;WITH d AS (
    SELECT @StartDate AS dt
    UNION ALL
    SELECT DATEADD(DAY, 1, dt)
    FROM d
    WHERE dt < @EndDate
)
INSERT INTO dbo.Dates
(
    DateKey, [Date], DayOfWeek, DayName, [Month], MonthName,
    Quarter, [Year], WeekOfYear, IsWeekend
)
SELECT
    CONVERT(INT, FORMAT(dt, 'yyyyMMdd')) AS DateKey,
    dt AS [Date],
    DATEPART(WEEKDAY, dt) AS DayOfWeek,
    DATENAME(WEEKDAY, dt) AS DayName,
    DATEPART(MONTH, dt) AS [Month],
    DATENAME(MONTH, dt) AS MonthName,
    DATEPART(QUARTER, dt) AS Quarter,
    DATEPART(YEAR, dt) AS [Year],
    DATEPART(ISO_WEEK, dt) AS WeekOfYear,
    CASE WHEN DATENAME(WEEKDAY, dt) IN ('Saturday','Sunday') THEN 1 ELSE 0 END AS IsWeekend
FROM d
OPTION (MAXRECURSION 1000);
GO

/* =========================================
   Verification checks (Acceptance Criteria)
========================================= */
SELECT COUNT(*) AS StoresCount FROM dbo.Stores;
SELECT COUNT(*) AS ProductsCount FROM dbo.Products;
SELECT MIN(DateKey) AS MinDateKey, MAX(DateKey) AS MaxDateKey, COUNT(*) AS DatesCount
FROM dbo.Dates;

-- Sample query: by region, category, time window
SELECT TOP 10
    st.Region,
    p.Category,
    d.[Date]
FROM dbo.Stores st
CROSS JOIN dbo.Products p
CROSS JOIN dbo.Dates d
ORDER BY d.[Date] DESC;
GO