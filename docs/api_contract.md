# Scrappy Market API Contract

## Purpose

This document defines the backend API contract for the Scrappy Market
FastAPI service.

The API provides a **controlled service layer between the orchestration
/ agent layer and the ScrappyMarket SQL Server database**. Agents and UI
components do **not connect directly to SQL Server**.

The backend exposes metadata and safe query endpoints over **approved
analytical views**.

------------------------------------------------------------------------

# Base URL

Local development:

`http://localhost:8000`

For Docker deployment, the base URL will be configured through
environment variables or service discovery.

------------------------------------------------------------------------

# Current Endpoints

## 1. Health Check

`GET /health`

### Purpose

Verifies that the FastAPI service is running.

### Example Response

``` json
{
  "status": "ok"
}
```

------------------------------------------------------------------------

## 2. Database Connectivity Check

`GET /db/ping`

### Purpose

Verifies that the FastAPI backend can connect to SQL Server.

### Example Response

``` json
{
  "db_response": 1
}
```

------------------------------------------------------------------------

## 3. Get Available Analytical Views

`GET /meta/views`

### Purpose

Returns the list of **approved analytical SQL views** that can be
queried by the API.

### Response

``` json
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

------------------------------------------------------------------------

## 4. Get Columns for a View

`GET /meta/columns/{view_name}`

### Purpose

Returns the list of columns available in a selected analytical view.

### Example Request

`GET /meta/columns/vw_sales_enriched`

### Response

``` json
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

### Error Behavior

-   Returns `404` or `400` if the view name is invalid or not approved.

### Used by

Lineage / Context Agent\
Query Builder Agent

------------------------------------------------------------------------

# 5. Execute Safe View Query

`POST /query/execute`\
Content-Type: `application/json`

### Purpose

Executes a **safe, validated query** against an approved analytical view
and returns structured JSON results.

The endpoint **does not accept raw SQL** from clients or agents.

Agents should use metadata endpoints (`/meta/views`,
`/meta/columns/{view_name}`) before constructing query requests when
schema information is uncertain.

------------------------------------------------------------------------

## Request Body

``` json
{
  "view_name": "vw_sales_daily_store",
  "filters": {
    "StoreID": 1
  },
  "limit": 20
}
```

------------------------------------------------------------------------

## Request Fields

-   **view_name** --- name of an approved analytical view\
-   **filters** --- optional key/value filters where keys must be valid
    columns in the selected view\
-   **limit** --- maximum number of rows to return

------------------------------------------------------------------------

## Example Response

``` json
{
  "success": true,
  "row_count": 20,
  "results": [
    {
      "DateKey": 20250801,
      "Date": "2025-08-01",
      "StoreID": 1,
      "Region": "Southeast",
      "City": "Atlanta",
      "UnitsSold": 17,
      "SalesAmount": 110.13,
      "CostAmount": 79.15,
      "MarginAmount": 30.98
    }
  ]
}
```

------------------------------------------------------------------------

## Validation Rules

The backend enforces the following rules:

-   Only approved analytical views can be queried
-   Clients cannot submit raw SQL
-   Filter columns must exist in the selected view
-   Filter values are passed to SQL Server using **parameterized
    queries**
-   Row limits are validated before query execution

------------------------------------------------------------------------

### Used by

Query Builder Agent\
Response Agent

------------------------------------------------------------------------

# Intended Agent Usage

## Lineage / Context Agent

The Lineage / Context Agent should call:

`GET /meta/views`\
`GET /meta/columns/{view_name}`

This allows the agent to dynamically understand:

-   what analytical views exist
-   what columns are available
-   which view best supports the investigation

------------------------------------------------------------------------

## Query Builder Agent

The Query Builder Agent should:

-   use metadata from the Lineage / Context Agent
-   select an appropriate approved view
-   identify valid filter columns
-   send a structured request to:

`POST /query/execute`

The Query Builder Agent **does not generate or execute raw SQL
directly**.

------------------------------------------------------------------------

## Response Agent

The Response Agent consumes the JSON returned by:

`POST /query/execute`

and converts it into:

-   natural language explanation
-   investigation reasoning
-   confidence score
-   business-friendly summary for the Streamlit UI

------------------------------------------------------------------------

# Example End-to-End Flow

User (Streamlit UI) │ ▼ Intent Agent │ ▼ Investigation Planner Agent │ ▼
Lineage / Context Agent │ ├── GET /meta/views └── GET
/meta/columns/{view_name} │ ▼ Query Builder Agent │ └── POST
/query/execute │ ▼ FastAPI Backend │ ▼ SQL Server │ ▼ JSON Results │ ▼
Response Agent │ ▼ Streamlit UI

In this flow, the query step uses a **structured API request
(`view_name`, `filters`, `limit`) rather than raw SQL text.**

------------------------------------------------------------------------

# Notes for Integration

-   Agents should query **approved analytical views** instead of raw
    tables
-   The API is the **only approved interface between agents and SQL
    Server**
-   The backend **does not accept raw SQL** from agents or UI clients
-   Query execution is restricted to **approved views and validated
    filter columns**
-   Future Docker deployment will configure API URLs via environment
    variables

------------------------------------------------------------------------

# Approved Views

The following analytical views are currently exposed through the API:

-   `vw_low_stock`
-   `vw_promo_sales_fact`
-   `vw_promotions_enriched`
-   `vw_sales_daily_product`
-   `vw_sales_daily_store`
-   `vw_sales_enriched`

------------------------------------------------------------------------

# Security Design

The backend enforces multiple safeguards:

-   Only **approved analytical views** are exposed
-   **Raw SQL execution is not permitted**
-   Column filters are **validated against view metadata**
-   Query parameters are executed using **parameterized SQL**
-   Row limits prevent large uncontrolled queries

This design prevents:

-   SQL injection
-   unauthorized table access
-   uncontrolled query execution
