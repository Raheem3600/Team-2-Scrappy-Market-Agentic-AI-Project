# Scrappy Market — Phase 1 Mock Retail Database Schema (SQL Server)

## 0) Purpose and Scope

This schema supports the Phase 1 MVP goal: enabling a multi-agent AI system to translate natural-language business questions into **structured investigation queries (SQL)** over a synthetic retail database.

**Domain (Phase 1 assumption):**  
Scrappy Market is a fictional **grocery / supermarket retailer (Albertsons-like)** operating multiple stores across regions.  
The dataset is synthetic and is designed to demonstrate investigation workflows (query generation and reasoning trace), **not** to deliver accurate business insights.

### Investigation workloads supported (Phase 1)
- **Top-N ranking**  
  _Example:_ “Top 5 products last month”
- **Store / Region comparison**  
  _Example:_ “Which region performed best in Q2?”
- **Promotion uplift**  
  _Example:_ “Did the promotion increase sales?”
- **Growth over time**  
  _Example:_ “Which products grew fastest over 6 months?”
- **Trend / seasonality**  
  _Example:_ “Show beverage sales trend over time”

**Time horizon:** 6 months  
**Granularity:** Daily facts (weekly/monthly analyses via SQL aggregation)  
**Target Sales volume:** ~5,000 rows (sparse daily combinations)

---

## 1) Entity Relationship Summary (High Level)

### Dimension-like tables
- **Stores** — store attributes (region, city)
- **Products** — product attributes (category, brand, price)
- **Dates** — calendar attributes (month, quarter, weekend)

### Fact-like tables
- **Sales** — daily aggregated sales per store and product
- **Inventory** — periodic inventory snapshots per store and product

### Promotions
- **Promotions** — campaign windows and discount policies
- **PromotionProducts** — bridge table mapping promotions to products (many-to-many)

---

## 2) Tables and Columns

### 2.1 Stores
**Purpose:**  
Store master data; supports store- and region-level comparisons.

**Columns**
- `StoreID` INT **PK**
- `StoreName` NVARCHAR(100) NOT NULL
- `City` NVARCHAR(100) NOT NULL
- `Region` NVARCHAR(50) NOT NULL  
  _(e.g., East, West, South)_
- `StoreType` NVARCHAR(50) NULL  
  _(e.g., Urban, Suburban, Rural)_

**Relationships**
- Stores (1) → Sales (many)
- Stores (1) → Inventory (many)

---

### 2.2 Products
**Purpose:**  
Product master data; supports category analysis and Top-N investigations.

**Columns**
- `ProductID` INT **PK**
- `ProductName` NVARCHAR(150) NOT NULL
- `Category` NVARCHAR(50) NOT NULL  
  _(e.g., Produce, Dairy, Snacks, Beverages, Frozen, Household)_
- `SubCategory` NVARCHAR(50) NULL
- `Brand` NVARCHAR(50) NULL
- `RegularPrice` DECIMAL(10,2) NOT NULL

**Relationships**
- Products (1) → Sales (many)
- Products (1) → Inventory (many)
- Products (many) ↔ Promotions (many) via PromotionProducts

---

### 2.3 Dates
**Purpose:**  
Date dimension to support time-based investigations (last month, quarter, weekends, etc.).

**Columns**
- `DateKey` INT **PK**  
  _(format: YYYYMMDD, e.g., 20250203)_
- `Date` DATE NOT NULL
- `DayOfWeek` TINYINT NOT NULL _(1–7)_
- `DayName` NVARCHAR(20) NOT NULL
- `Month` TINYINT NOT NULL _(1–12)_
- `MonthName` NVARCHAR(20) NOT NULL
- `Quarter` TINYINT NOT NULL _(1–4)_
- `Year` INT NOT NULL
- `WeekOfYear` TINYINT NOT NULL
- `IsWeekend` BIT NOT NULL

**Relationships**
- Dates (1) → Sales (many)
- Dates (1) → Inventory (many)
- Dates (1) → Promotions (many) via StartDateKey / EndDateKey

---

### 2.4 Promotions
**Purpose:**  
Campaign metadata (time window and discount policy); supports promotion uplift investigations.

**Columns**
- `PromotionID` INT **PK** IDENTITY(1,1)
- `PromotionName` NVARCHAR(100) NOT NULL
- `StartDateKey` INT NOT NULL  
  **FK → Dates(DateKey)**
- `EndDateKey` INT NOT NULL  
  **FK → Dates(DateKey)**
- `DiscountType` NVARCHAR(20) NOT NULL  
  _(‘PERCENT’, ‘FIXED’)_
- `DiscountValue` DECIMAL(10,2) NOT NULL  
  _(e.g., 0.20 for 20% if PERCENT)_

**Notes**
- `StartDateKey` must be less than or equal to `EndDateKey`  
  _(can be enforced via validation or check constraint)_

---

### 2.5 PromotionProducts (Bridge)
**Purpose:**  
Maps promotions to products (many-to-many relationship).

**Columns**
- `PromotionID` INT NOT NULL  
  **FK → Promotions(PromotionID)**
- `ProductID` INT NOT NULL  
  **FK → Products(ProductID)**

**Keys**
- Composite **PK** (`PromotionID`, `ProductID`)

---

### 2.6 Sales
**Purpose:**  
Primary fact table for investigation. Stores **daily aggregated sales per store and product**  
(not customer-level transactions).

**Columns**
- `SaleID` INT **PK** IDENTITY(1,1)
- `DateKey` INT NOT NULL  
  **FK → Dates(DateKey)**
- `StoreID` INT NOT NULL  
  **FK → Stores(StoreID)**
- `ProductID` INT NOT NULL  
  **FK → Products(ProductID)**

**Measures**
- `UnitsSold` INT NOT NULL
- `SalesAmount` DECIMAL(10,2) NOT NULL  
  _(revenue)_
- `CostAmount` DECIMAL(10,2) NOT NULL
- `MarginAmount` DECIMAL(10,2) NOT NULL  
  _(SalesAmount − CostAmount; stored or computed)_
- `WasOnPromotion` BIT NOT NULL  
  _(1 if product is in an active promotion on DateKey, else 0)_

**Design notes**
- Data is **sparse** (not every store/product every day)
- Targets ~5,000 rows over 6 months
- Supports Top-N, growth (% change), and promotion comparisons

---

### 2.7 Inventory
**Purpose:**  
Inventory snapshots to provide stock context during investigations  
(minimal usage in Phase 1).

**Columns**
- `InventoryID` INT **PK** IDENTITY(1,1)
- `DateKey` INT NOT NULL  
  **FK → Dates(DateKey)**
- `StoreID` INT NOT NULL  
  **FK → Stores(StoreID)**
- `ProductID` INT NOT NULL  
  **FK → Products(ProductID)**

**Measures**
- `OnHandQuantity` INT NOT NULL
- `ReorderPoint` INT NOT NULL

**Design notes**
- Inventory can be loaded as **weekly or monthly snapshots**
- Daily inventory for all products is not required for Phase 1

---

## 3) Key Investigation Patterns Supported (Examples)

- **Top-N Products**  
  “Top 5 products by sales last month”  
  _(Sales + Products + Dates)_

- **Region Comparison**  
  “Which region had the highest revenue in Q2?”  
  _(Sales + Stores + Dates)_

- **Promotion Uplift**  
  “Did ‘Summer Beverages Sale’ increase sales?”  
  _(Promotions + PromotionProducts + Sales + Dates)_

- **Growth Over Time**  
  “Which products grew fastest across 6 months?”  
  _(Early-period vs late-period aggregates)_

- **Trend / Seasonality**  
  “Show beverage sales trend over time”  
  _(Time-series rollups by week or month)_

---

## 4) Synthetic Data Shaping Rules (Phase 1)

Synthetic data will include **designed signals** to ensure investigations produce meaningful results:
- Clear top-selling products (Top-N)
- Region-level performance differences (e.g., South vs East vs West)
- Promotions that increase units sold during campaign windows
- A small set of fast-growing products over the 6-month period
- Category-level seasonal trends
