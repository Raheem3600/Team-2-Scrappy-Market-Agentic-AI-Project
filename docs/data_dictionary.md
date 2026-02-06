# Scrappy Market — Phase 1 Data Dictionary

This data dictionary describes the meaning and intended usage of tables and columns in the Phase 1 synthetic retail database.  
The dictionary supports explainability for Agentic AI–driven investigation workflows.

---

## STORES
**Purpose:** Master list of retail stores; used for store- and region-level comparisons.

| Column | Description |
|------|------------|
| StoreID | Unique identifier for a store |
| StoreName | Human-readable store name |
| City | City where the store operates |
| Region | Geographic region (e.g., East, West, South) |
| StoreType | Store classification (Urban, Suburban, Rural) |

---

## PRODUCTS
**Purpose:** Master list of products sold by Scrappy Market.

| Column | Description |
|------|------------|
| ProductID | Unique identifier for a product |
| ProductName | Product display name |
| Category | High-level product category (Produce, Dairy, Beverages, etc.) |
| SubCategory | Optional sub-category within a category |
| Brand | Brand name (if applicable) |
| RegularPrice | Standard retail price before discounts |

---

## DATES
**Purpose:** Calendar dimension supporting time-based filtering and aggregation.

| Column | Description |
|------|------------|
| DateKey | Surrogate date key in YYYYMMDD format |
| Date | Calendar date |
| DayOfWeek | Numeric day of week (1–7) |
| DayName | Name of the day (Monday–Sunday) |
| Month | Numeric month (1–12) |
| MonthName | Month name |
| Quarter | Quarter of the year (1–4) |
| Year | Calendar year |
| WeekOfYear | Week number within the year |
| IsWeekend | Indicates whether the date falls on a weekend |

---

## PROMOTIONS
**Purpose:** Defines promotional campaigns and their active time windows.

| Column | Description |
|------|------------|
| PromotionID | Unique identifier for a promotion |
| PromotionName | Campaign name |
| StartDateKey | Start date of the promotion |
| EndDateKey | End date of the promotion |
| DiscountType | Discount type (PERCENT or FIXED) |
| DiscountValue | Discount amount (e.g., 0.20 = 20% if PERCENT) |

---

## PROMOTION_PRODUCTS
**Purpose:** Bridge table mapping promotions to products.

| Column | Description |
|------|------------|
| PromotionID | Identifier of the promotion |
| ProductID | Identifier of the product included in the promotion |

---

## SALES
**Purpose:** Core fact table capturing daily aggregated sales activity.

| Column | Description |
|------|------------|
| SaleID | Unique identifier for a sales record |
| DateKey | Date of sale |
| StoreID | Store where the sale occurred |
| ProductID | Product sold |
| UnitsSold | Number of units sold |
| SalesAmount | Total revenue for the sale |
| CostAmount | Cost associated with sold units |
| MarginAmount | SalesAmount minus CostAmount |
| WasOnPromotion | Indicates if the sale occurred during an active promotion |

**Notes:**
- Each record represents aggregated daily sales per store and product.
- Not every store/product combination exists every day (sparse data).

---

## INVENTORY
**Purpose:** Snapshot of on-hand inventory for context during investigations.

| Column | Description |
|------|------------|
| InventoryID | Unique identifier for inventory snapshot |
| DateKey | Snapshot date |
| StoreID | Store holding the inventory |
| ProductID | Product in inventory |
| OnHandQuantity | Units available at snapshot time |
| ReorderPoint | Threshold below which restocking is needed |

**Notes:**
- Inventory is modeled as a snapshot, not a transaction log.
- Used to explain sales behavior, not to manage supply chain flows.

---

## General Notes
- All data is synthetic and designed for investigation workflows, not real analytics.
- Phase 1 focuses on explainability and SQL generation, not business accuracy.

## How Agentic AI Uses This Data (Phase 1)

The Agentic AI system uses this schema and data dictionary to translate natural-language business questions into structured investigation workflows.

At a high level, the agent follows these steps:

1. **Identify the investigation intent**  
   Examples include Top-N ranking, region comparison, promotion uplift, growth analysis, or trend analysis.

2. **Select relevant entities and metrics**  
   - Uses **Sales** as the primary evidence table.
   - Uses **Products** and **Stores** to define the analysis scope.
   - Uses **Dates** to resolve time windows such as “last month” or “Q2”.

3. **Resolve promotional context (if applicable)**  
   - Uses **Promotions** to determine campaign windows.
   - Uses **PromotionProducts** to identify which products were affected.
   - Compares sales before and during promotion periods.

4. **Generate investigation SQL queries**  
   - Constructs SQL queries using joins across Sales, Dates, Products, and Stores.
   - Applies grouping, aggregation, and ordering based on investigation intent.

5. **Provide explainable reasoning**  
   - Explains which tables were used and why.
   - Describes how time windows, filters, and comparisons were applied.
   - Uses **Inventory snapshots** when needed to provide context for unusual sales behavior.

This design enables the agent to demonstrate *how* an investigation would be performed, rather than producing definitive business conclusions, which aligns with the Phase 1 MVP scope.

