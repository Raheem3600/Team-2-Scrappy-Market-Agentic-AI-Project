---
config:
  layout: dagre
---
erDiagram
  STORES ||--o{ SALES : has
  PRODUCTS ||--o{ SALES : has
  DATES ||--o{ SALES : occurs_on

  STORES ||--o{ INVENTORY : has
  PRODUCTS ||--o{ INVENTORY : has
  DATES ||--o{ INVENTORY : snapshot_on

  PROMOTIONS ||--o{ PROMOTION_PRODUCTS : includes
  PRODUCTS ||--o{ PROMOTION_PRODUCTS : included_in
  DATES ||--o{ PROMOTIONS : start_end

  STORES {
    int StoreID PK
    string StoreName
    string City
    string Region
    string StoreType
  }

  PRODUCTS {
    int ProductID PK
    string ProductName
    string Category
    string SubCategory
    string Brand
    decimal RegularPrice
  }

  DATES {
    int DateKey PK
    date Date
    tinyint DayOfWeek
    string DayName
    tinyint Month
    string MonthName
    tinyint Quarter
    int Year
    tinyint WeekOfYear
    boolean IsWeekend
  }

  PROMOTIONS {
    int PromotionID PK
    string PromotionName
    int StartDateKey FK
    int EndDateKey FK
    string DiscountType
    decimal DiscountValue
  }

  PROMOTION_PRODUCTS {
    int PromotionID PK, FK
    int ProductID PK, FK
  }

  SALES {
    int SaleID PK
    int DateKey FK
    int StoreID FK
    int ProductID FK
    int UnitsSold
    decimal SalesAmount
    decimal CostAmount
    decimal MarginAmount
    boolean WasOnPromotion
  }

  INVENTORY {
    int InventoryID PK
    int DateKey FK
    int StoreID FK
    int ProductID FK
    int OnHandQuantity
    int ReorderPoint
  }

  USERS {
    int UserID PK
    string Username
    string Email
    string PasswordHash
    string Role
    datetime CreatedAt
    boolean IsActive
  }
