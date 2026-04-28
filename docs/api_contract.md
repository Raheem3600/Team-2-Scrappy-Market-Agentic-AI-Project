# Scrappy Market API Contract

## Purpose

This document defines the backend API contract for the Scrappy Market FastAPI service.

The API provides a **controlled service layer between the orchestration / agent layer and the ScrappyMarket SQL Server database**. Agents and UI components do **not connect directly to SQL Server**.

The backend exposes metadata, safe row-level query endpoints, and controlled analytical query endpoints over **approved analytical views**.

---

## Base URL

Local development:

```text
http://localhost:8000
```

For Docker deployment, the base URL will be configured through environment variables or service discovery.

---

## Current Endpoints

## 1. Health Check

`GET /health`

### Purpose

Verifies that the FastAPI service is running.

### Example Response

```json
{
  "status": "ok"
}
```

---

## 2. Database Connectivity Check

`GET /db/ping`

### Purpose

Verifies that the FastAPI backend can connect to SQL Server.

### Example Response

```json
{
  "db_response": 1
}
```

---

## 3. Get Available Analytical Views

`GET /meta/views`

### Purpose

Returns the list of **approved analytical SQL views** that can be queried by the API.

### Example Response

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

### Used By

- Lineage / Context Agent
- Query Builder Agent

---

## 4. Get Columns for a View

`GET /meta/columns/{view_name}`

### Purpose

Returns the list of columns available in a selected analytical view.

### Example Request

```text
GET /meta/columns/vw_sales_enriched
```

### Example Response

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

### Error Behavior

- Returns `400` or `404` if the view name is invalid or not approved.

### Used By

- Lineage / Context Agent
- Query Builder Agent

---

## 5. Execute Safe View Query

`POST /query/execute`

Content-Type: `application/json`

### Purpose

Executes a **safe, validated row-level query** against an approved analytical view and returns structured JSON results.

This endpoint is intended for simple filtered retrieval.

The endpoint **does not accept raw SQL** from clients or agents.

Agents should use metadata endpoints such as `/meta/views` and `/meta/columns/{view_name}` before constructing query requests when schema information is uncertain.

### Request Body

```json
{
  "view_name": "vw_sales_daily_store",
  "filters": {
    "StoreID": 1
  },
  "limit": 20
}
```

### Request Fields

- **view_name** — name of an approved analytical view
- **filters** — optional key/value filters where keys must be valid columns in the selected view
- **limit** — maximum number of rows to return

### Example Response

```json
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



### Example 6: Year-over-Year Trend

Natural language question:

```text
Show year-over-year sales trend.
```

Request:

```json
{
  "analysis_type": "year_over_year",
  "view_name": "vw_sales_enriched",
  "metrics": ["SalesAmount", "MarginAmount"],
  "group_by": ["Year"],
  "filters": {},
  "limit": 10
}
```

Response:

```json
{
  "success": true,
  "analysis_type": "year_over_year",
  "row_count": 2,
  "results": [
    {
      "Year": 2025,
      "TotalSalesAmount": 135248.79,
      "TotalMarginAmount": 38560.53,
      "YoYChangePct": null
    },
    {
      "Year": 2026,
      "TotalSalesAmount": 28376.25,
      "TotalMarginAmount": 8039.73,
      "YoYChangePct": -79.02
    }
  ]
}
```

### Interpretation Note

`YoYChangePct` represents the percentage change compared to the previous year.

Because the dataset may contain **partial-year data**, YoY results should be interpreted carefully unless equivalent time periods are compared.


### Validation Rules

The backend enforces the following rules:

- Only approved analytical views can be queried
- Clients cannot submit raw SQL
- Filter columns must exist in the selected view
- Filter values are passed to SQL Server using **parameterized queries**
- Row limits are validated before query execution

### Used By

- Query Builder Agent
- Response Agent

---

## 6. Execute Analytical Query

`POST /query/analyze`

Content-Type: `application/json`

### Purpose

Executes **controlled analytical queries** such as:

- region breakdown
- Top-N ranking
- promotion comparison
- time-based trends such as month-over-month analysis

This endpoint extends the API from **row-level retrieval** to **analytical query execution**.

The endpoint enables aggregation, grouping, sorting, and comparison-style queries while maintaining the same safety guarantees as `/query/execute`.

The endpoint **does not accept raw SQL** from clients or agents.

### Request Body

```json
{
  "analysis_type": "region_breakdown",
  "view_name": "vw_sales_enriched",
  "metrics": ["SalesAmount", "UnitsSold"],
  "group_by": ["Region"],
  "filters": {},
  "sort_by": "SalesAmount",
  "sort_direction": "desc",
  "limit": 10
}
```

### Request Fields

- **analysis_type** — type of analytical query to execute
- **view_name** — approved analytical view
- **metrics** — numeric fields to aggregate using `SUM`
- **group_by** — dimensions used for grouping
- **filters** — optional key/value filters where keys must be valid columns in the selected view
- **sort_by** — optional metric used for ordering results
- **sort_direction** — sort direction; supported values are `asc` and `desc`
- **limit** — maximum number of rows to return

### Supported Analysis Types

- `region_breakdown`
- `top_n`
- `promotion_comparison`
- `month_over_month`
- `year_over_year`

---

### Example 1: Region Breakdown

Natural language question:

```text
Show me the sales breakdown by region.
```

Request:

```json
{
  "analysis_type": "region_breakdown",
  "view_name": "vw_sales_enriched",
  "metrics": ["SalesAmount", "UnitsSold"],
  "group_by": ["Region"],
  "filters": {},
  "limit": 10
}
```

Response:

```json
{
  "success": true,
  "analysis_type": "region_breakdown",
  "row_count": 4,
  "results": [
    {
      "Region": "Southeast",
      "TotalSalesAmount": 89233.21,
      "TotalUnitsSold": 22645
    },
    {
      "Region": "South",
      "TotalSalesAmount": 38824.82,
      "TotalUnitsSold": 9718
    }
  ]
}
```

---

### Example 2: Top-N Products

Natural language question:

```text
What are the top 5 products by sales?
```

Request:

```json
{
  "analysis_type": "top_n",
  "view_name": "vw_sales_enriched",
  "metrics": ["SalesAmount", "UnitsSold"],
  "group_by": ["ProductID", "ProductName", "Category"],
  "filters": {},
  "sort_by": "SalesAmount",
  "sort_direction": "desc",
  "limit": 5
}
```

Response:

```json
{
  "success": true,
  "analysis_type": "top_n",
  "row_count": 5,
  "results": [
    {
      "ProductID": 603,
      "ProductName": "Olive Oil (16.9 oz)",
      "Category": "Pantry",
      "TotalSalesAmount": 12829.54,
      "TotalUnitsSold": 1368
    }
  ]
}
```

---

### Example 3: Top-N Products by Region

Natural language question:

```text
What are the top 5 products by sales in the Southeast region?
```

Request:

```json
{
  "analysis_type": "top_n",
  "view_name": "vw_sales_enriched",
  "metrics": ["SalesAmount", "UnitsSold"],
  "group_by": ["ProductID", "ProductName", "Category"],
  "filters": {
    "Region": "Southeast"
  },
  "sort_by": "SalesAmount",
  "sort_direction": "desc",
  "limit": 5
}
```

Response:

```json
{
  "success": true,
  "analysis_type": "top_n",
  "row_count": 5,
  "results": [
    {
      "ProductID": 603,
      "ProductName": "Olive Oil (16.9 oz)",
      "Category": "Pantry",
      "TotalSalesAmount": 6925.8,
      "TotalUnitsSold": 738
    }
  ]
}
```

---

### Example 4: Promotion Comparison

Natural language question:

```text
Do promotions increase sales?
```

Request:

```json
{
  "analysis_type": "promotion_comparison",
  "view_name": "vw_sales_enriched",
  "metrics": ["SalesAmount", "UnitsSold", "MarginAmount"],
  "group_by": ["WasOnPromotion"],
  "filters": {},
  "limit": 10
}
```

Response:

```json
{
  "success": true,
  "analysis_type": "promotion_comparison",
  "row_count": 2,
  "results": [
    {
      "WasOnPromotion": false,
      "TotalSalesAmount": 158845.27,
      "TotalUnitsSold": 40303,
      "TotalMarginAmount": 45230.9
    },
    {
      "WasOnPromotion": true,
      "TotalSalesAmount": 4779.77,
      "TotalUnitsSold": 1316,
      "TotalMarginAmount": 1369.36
    }
  ]
}
```

### Interpretation Note

Promotion comparison results should be interpreted in context. A lower total sales value for promotion rows may indicate that the synthetic dataset contains fewer promotion transactions, not necessarily that promotions are ineffective.

---

### Example 5: Month-over-Month Trend

Natural language question:

```text
Show monthly sales trend over time.
```

Request:

```json
{
  "analysis_type": "month_over_month",
  "view_name": "vw_sales_enriched",
  "metrics": ["SalesAmount"],
  "group_by": ["Year", "Month"],
  "filters": {},
  "limit": 12
}
```

Response:

```json
{
  "success": true,
  "analysis_type": "month_over_month",
  "row_count": 6,
  "results": [
    {
      "Year": 2025,
      "Month": 8,
      "TotalSalesAmount": 26670.96,
      "MoMChangePct": null
    },
    {
      "Year": 2025,
      "Month": 9,
      "TotalSalesAmount": 27086.2,
      "MoMChangePct": 1.56
    },
    {
      "Year": 2025,
      "Month": 10,
      "TotalSalesAmount": 26650.54
    },
    {
      "Year": 2025,
      "Month": 11,
      "TotalSalesAmount": 26891.65
    },
    {
      "Year": 2025,
      "Month": 12,
      "TotalSalesAmount": 27949.44
    },
    {
      "Year": 2026,
      "Month": 1,
      "TotalSalesAmount": 28376.25
    }
  ]
}
```



### Example 6: Year-over-Year Trend

Natural language question:

```text
Show year-over-year sales trend.
```

Request:

```json
{
  "analysis_type": "year_over_year",
  "view_name": "vw_sales_enriched",
  "metrics": ["SalesAmount", "MarginAmount"],
  "group_by": ["Year"],
  "filters": {},
  "limit": 10
}
```

Response:

```json
{
  "success": true,
  "analysis_type": "year_over_year",
  "row_count": 2,
  "results": [
    {
      "Year": 2025,
      "TotalSalesAmount": 135248.79,
      "TotalMarginAmount": 38560.53,
      "YoYChangePct": null
    },
    {
      "Year": 2026,
      "TotalSalesAmount": 28376.25,
      "TotalMarginAmount": 8039.73,
      "YoYChangePct": -79.02
    }
  ]
}
```

### Interpretation Note

`YoYChangePct` represents the percentage change compared to the previous year.

Because the dataset may contain **partial-year data**, YoY results should be interpreted carefully unless equivalent time periods are compared.


### Validation Rules

The backend enforces the following rules:

- Only approved analytical views can be queried
- Only supported analysis types can be used
- Only valid columns can be used in `metrics`, `group_by`, and `filters`
- Aggregation is restricted to `SUM`
- Sorting direction must be `asc` or `desc`
- Query limits are validated before execution
- Raw SQL is not accepted from agents or clients

### Used By

- Query Builder Agent
- Response Agent

### Design Note

This endpoint enables **advanced analytical queries** while maintaining controlled backend query generation.

It supports:

- grouped summaries
- ranking
- segment comparisons
- time-series summaries

while maintaining:

- security through no raw SQL
- consistency through approved views
- safety through validation and parameterized execution

---

## Intended Agent Usage

### Lineage / Context Agent

The Lineage / Context Agent should call:

```text
GET /meta/views
GET /meta/columns/{view_name}
```

This allows the agent to dynamically understand:

- what analytical views exist
- what columns are available
- which view best supports the investigation

---

### Query Builder Agent

The Query Builder Agent should:

- use metadata from the Lineage / Context Agent
- select an appropriate approved view
- identify valid filter columns, metrics, and grouping fields
- send a structured request to the correct API endpoint

Supported query endpoints:

```text
POST /query/execute   # row-level retrieval
POST /query/analyze   # analytical queries
```

The Query Builder Agent **does not generate or execute raw SQL directly**.

---

### Response Agent

The Response Agent consumes JSON returned by:

```text
POST /query/execute
POST /query/analyze
```

and converts it into:

- natural language explanation
- investigation reasoning
- confidence score
- business-friendly summary for the Streamlit UI

---

## Example End-to-End Flow

```text
User (Streamlit UI)
        |
        v
Intent Agent
        |
        v
Investigation Planner Agent
        |
        v
Lineage / Context Agent
        |
        |-- GET /meta/views
        |-- GET /meta/columns/{view_name}
        |
        v
Query Builder Agent
        |
        |-- POST /query/execute
        |-- POST /query/analyze
        |
        v
FastAPI Backend
        |
        v
SQL Server
        |
        v
JSON Results
        |
        v
Response Agent
        |
        v
Streamlit UI
```

In this flow, query execution uses **structured API requests** rather than raw SQL text.

---

## Notes for Integration

- Agents should query **approved analytical views** instead of raw tables
- The API is the **only approved interface between agents and SQL Server**
- The backend **does not accept raw SQL** from agents or UI clients
- `/query/execute` supports safe row-level retrieval
- `/query/analyze` supports controlled analytical queries
- Query execution is restricted to approved views and validated columns
- Future Docker deployment will configure API URLs through environment variables

---

## Approved Views

The following analytical views are currently exposed through the API:

- `vw_low_stock`
- `vw_promo_sales_fact`
- `vw_promotions_enriched`
- `vw_sales_daily_product`
- `vw_sales_daily_store`
- `vw_sales_enriched`

---

## Security Design

The backend enforces multiple safeguards:

- Only **approved analytical views** are exposed
- **Raw SQL execution is not permitted**
- View names are validated
- Column names are validated
- Filter columns are validated against approved view metadata
- Query parameters are executed using **parameterized SQL**
- Row limits prevent large uncontrolled queries
- Analytical query generation is controlled by backend-defined patterns

This design prevents:

- SQL injection
- unauthorized table access
- uncontrolled query execution
- unsafe agent-generated SQL
