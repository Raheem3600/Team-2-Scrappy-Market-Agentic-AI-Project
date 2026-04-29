from app.services.db_service import execute_select_query


ALLOWED_ANALYSIS_TYPES = {
    "region_breakdown",
    "top_n",
    "promotion_comparison",
    "month_over_month",
    "year_over_year",
}

ALLOWED_VIEWS = {
    "vw_sales_enriched",
    "vw_sales_daily_store",
    "vw_sales_daily_product",
    "vw_promo_sales_fact",
}

VALID_COLUMNS = {
    "vw_sales_enriched": {
        "Region",
        "SalesAmount",
        "UnitsSold",
        "MarginAmount",
        "StoreID",
        "StoreName",
        "City",
        "ProductID",
        "ProductName",
        "Category",
        "WasOnPromotion",
        "Year",
        "Month",
        "Quarter",
        "Date",
    },
    "vw_sales_daily_product": {
        "DateKey",
        "ProductID",
        "ProductName",
        "Category",
        "SalesAmount",
        "UnitsSold"
    },
    "vw_sales_daily_store": {
        "DateKey",
        "StoreID",
        "StoreName",
        "Region",
        "SalesAmount",
        "UnitsSold"
    }
}


def execute_analysis(request):
    """
    Executes controlled analytical queries.
    This does NOT accept raw SQL from agents or clients.
    """

    if request.analysis_type not in ALLOWED_ANALYSIS_TYPES:
        raise ValueError(f"Analysis type '{request.analysis_type}' is not supported.")

    if request.view_name not in ALLOWED_VIEWS:
        raise ValueError(f"View '{request.view_name}' is not allowed for analysis.")

    valid_columns = VALID_COLUMNS.get(request.view_name, set())

    for column in request.group_by:
        if column not in valid_columns:
            raise ValueError(
                f"Invalid group_by column '{column}' for view '{request.view_name}'."
            )

    for metric in request.metrics:
        if metric not in valid_columns:
            raise ValueError(
                f"Invalid metric column '{metric}' for view '{request.view_name}'."
            )

    for column in request.filters.keys():
        if column not in valid_columns:
            raise ValueError(
                f"Invalid filter column '{column}' for view '{request.view_name}'."
            )

    select_parts = []

    for column in request.group_by:
        select_parts.append(column)

    for metric in request.metrics:
        select_parts.append(f"SUM({metric}) AS Total{metric}")

    select_clause = ", ".join(select_parts)

    sql = f"SELECT TOP {int(request.limit)} {select_clause} FROM dbo.{request.view_name}"

    params = []
    conditions = []

    if request.filters:
        for column, value in request.filters.items():
            if isinstance(value, list):
                if not value:
                    raise ValueError(f"Filter list for '{column}' cannot be empty.")

                placeholders = ", ".join(["?"] * len(value))
                conditions.append(f"{column} IN ({placeholders})")
                params.extend(value)
            else:
                conditions.append(f"{column} = ?")
                params.append(value)

    if conditions:
        sql += " WHERE " + " AND ".join(conditions)

    if request.group_by:
        sql += " GROUP BY " + ", ".join(request.group_by)

    if request.analysis_type == "month_over_month":
        sql += " ORDER BY Year, Month"

    elif request.analysis_type == "year_over_year":
        sql += " ORDER BY Year"

    elif request.metrics:
        sort_column = request.sort_by or request.metrics[0]
        direction = request.sort_direction.upper()

        if direction not in {"ASC", "DESC"}:
            raise ValueError("sort_direction must be 'asc' or 'desc'")

        sql += f" ORDER BY Total{sort_column} {direction}"

    results = execute_select_query(sql, params)

    if request.analysis_type == "month_over_month" and results:
        results[0]["MoMChangePct"] = None

        for i in range(1, len(results)):
            prev = results[i - 1]["TotalSalesAmount"]
            curr = results[i]["TotalSalesAmount"]

            if prev and prev != 0:
                results[i]["MoMChangePct"] = round(((curr - prev) / prev) * 100, 2)
            else:
                results[i]["MoMChangePct"] = None

    if request.analysis_type == "year_over_year" and results:
        results[0]["YoYChangePct"] = None

        for i in range(1, len(results)):
            prev = results[i - 1]["TotalSalesAmount"]
            curr = results[i]["TotalSalesAmount"]

            if prev and prev != 0:
                results[i]["YoYChangePct"] = round(((curr - prev) / prev) * 100, 2)
            else:
                results[i]["YoYChangePct"] = None

    return {
        "results": results,
        "sql": sql,
        "params": params
    }