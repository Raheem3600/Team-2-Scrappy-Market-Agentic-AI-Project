# Scrappy Market API Contract

## Purpose

This document defines the backend API contract used by the LangGraph agent layer to interact with the ScrappyMarket SQL Server database.

The API acts as the controlled interface between agents and the data layer. Agents **do not connect directly to SQL Server**.

---

# Base URL

For local development:http://localhost:8000


For Docker deployment, the base URL may be updated through environment variables.

---

# Current Endpoints

## 1. Health Check
GET /health

### Purpose
Verifies that the FastAPI service is running.

### Response

```json
{
  "status": "ok"
}

```
## 2. Database Connectivity Check
GET /db/ping

### Purpose
Verifies that the FastAPI backend can connect to SQL Server.

### Response
```json
{
  "db_response": 1
}
```

## 3. Get Available Analytical Views
GET /meta/views

### Purpose

Returns the list of SQL views available for agent-based investigation.

### Response

```json
{
  "views": [
    "vw_low_stock",
    "vw_promo_sales_fact",
    "vw_promotions_enriched",
    "vw_sales_daily_product",
    "vw_sales_daily_store",
    "vw_sales_enriched"
  ]
}
```

### Used by

Lineage / Context Agent

## 4. Get Columns for a View
GET /meta/columns/{view_name}

### Purpose

Returns the list of columns available in a selected analytical view.

### Example Request
GET /meta/columns/vw_sales_enriched

### Response
```json
{
  "view": "vw_sales_enriched",
  "columns": [
    "SaleID",
    "DateKey",
    "Date",
    "DayOfWeek",
    "DayName",
    "Month",
    "MonthName",
    "Quarter",
    "Year",
    "WeekOfYear",
    "IsWeekend",
    "StoreID",
    "StoreName",
    "City",
    "Region",
    "StoreType",
    "ProductID",
    "ProductName",
    "Category",
    "SubCategory",
    "Brand",
    "RegularPrice",
    "UnitsSold",
    "SalesAmount",
    "CostAmount",
    "MarginAmount",
    "WasOnPromotion"
  ]
}
```
### Used by

Lineage / Context Agent

Query Builder Agent

## 5. Execute SQL Query

POST /query/execute
Content-Type: application/json

### Purpose
Receives a validated SQL SELECT query, executes it against SQL Server, and returns results in structured JSON format.

### Request Body

```json
{
  "sql": "SELECT TOP 5 ProductName, SalesAmount, Region FROM vw_sales_enriched"
}

```

### Example Response
```json
{
  "row_count": 5,
  "results": [
    {
      "ProductName": "Bananas",
      "SalesAmount": 123.45,
      "Region": "Southeast"
    }
  ]
}
```
---
### Current Validation Rules

Only SELECT queries are allowed

Dangerous SQL keywords are blocked:
INSERT
UPDATE
DELETE
DROP
ALTER
TRUNCATE
CREATE
---

### Used by

Query Builder Agent

Response Agent

---

## Intended Agent Usage
### Lineage / Context Agent

The Lineage / Context Agent should call:

GET /meta/views
GET /meta/columns/{view_name}

This allows the agent to dynamically understand:

-what analytical views exist

-what columns are available

-which view best supports the investigation
---

### Query Builder Agent

The Query Builder Agent should:

-use metadata from the Lineage Agent

-generate a SQL SELECT query

-send that query to:

POST /query/execute

The Query Builder Agent does not execute SQL directly.
---

### Response Agent

The Response Agent consumes the JSON returned by:

POST /query/execute

and converts it into:

-natural language explanation

-investigation reasoning

-confidence score

-optional SQL display for the Streamlit UI
---

## Example End-to-End Flow

User (Streamlit UI)
        │
        ▼
Intent Agent
        │
        ▼
Investigation Planner Agent
        │
        ▼
Lineage / Context Agent
        │
        ├── GET /meta/views
        └── GET /meta/columns/{view_name}
        │
        ▼
Query Builder Agent
        │
        └── POST /query/execute
        │
        ▼
FastAPI Backend
        │
        ▼
SQL Server
        │
        ▼
JSON Results
        │
        ▼
Response Agent
        │
        ▼
Streamlit UI

---
## Notes for Integration

-Agents should query analytical views instead of raw tables.

-The API is the only approved interface between agents and SQL Server.

-The backend ensures safe SQL execution.

-Future Docker deployment will configure API URLs via environment variables.