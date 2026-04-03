from app.services.db_service import execute_select_query

ALLOWED_VIEWS = {
    "vw_sales_daily_store",
    "vw_low_stock",
    "vw_sales_enriched",
    "vw_promotions_enriched",
    "vw_sales_daily_product",
    "vw_promo_sales_fact",
}

VIEW_COLUMNS = {
    "vw_sales_daily_store": {
        "DateKey", "StoreID", "StoreName", "Channel",
        "TotalSalesAmount", "TotalQuantitySold", "TransactionCount", "Region", "UnitsSold"
    },
    "vw_low_stock": {
        "StoreID", "StoreName", "ProductID", "ProductName",
        "OnHandQuantity", "ReorderPoint"
    },
    "vw_sales_enriched": {
        "SalesID", "DateKey", "StoreID", "StoreName", "Region", "City",
        "ProductID", "ProductName", "Category", "QuantitySold",
        "SalesAmount", "UnitPrice", "PromotionID", "PromotionName",
        "DiscountPct", "Channel", "WasOnPromotion", "UnitsSold"
    },
    "vw_promotions_enriched": {
        "PromotionID", "PromotionName", "DiscountPct",
        "StartDateKey", "EndDateKey"
    },
    "vw_sales_daily_product": {
        "DateKey", "ProductID", "ProductName", "Category",
        "TotalSalesAmount", "TotalQuantitySold", "UnitsSold"
    },
    "vw_promo_sales_fact": {
        "SalesID", "DateKey", "StoreID", "ProductID", "PromotionID",
        "QuantitySold", "SalesAmount", "UnitPrice"
    },
}


def execute_safe_query(
    view_name: str,
    metric_column: str,
    filters: dict,
    order_by: str | None,
    limit: int,
    aggregation: str | None = None,
    group_by: str | None = None,
):
    if view_name not in ALLOWED_VIEWS:
        raise ValueError(f"View '{view_name}' is not allowed.")

    valid_columns = VIEW_COLUMNS.get(view_name, set())

    # Validate filters
    for column in filters.keys():
        if column not in valid_columns:
            raise ValueError(f"Invalid filter column '{column}' for view '{view_name}'.")

    # Validate group_by
    if group_by and group_by not in valid_columns:
        raise ValueError(f"Invalid group_by column '{group_by}'.")

    # Validate metric column
    if metric_column not in valid_columns:
        raise ValueError(f"Invalid metric column '{metric_column}'.")

    params = []

    # ==============================
    # SELECT CLAUSE
    # ==============================
    if aggregation:
        if group_by:
            sql = f"SELECT TOP {int(limit)} {group_by}, {aggregation}({metric_column}) AS value FROM dbo.{view_name}"
        else:
            sql = f"SELECT {aggregation}({metric_column}) AS value FROM dbo.{view_name}"
    else:
        sql = f"SELECT TOP {int(limit)} * FROM dbo.{view_name}"

    # ==============================
    # WHERE CLAUSE
    # ==============================
    if filters:
        conditions = []
        for column, value in filters.items():
            if value is None:
                continue  # 🔥 skip NULL filters
            conditions.append(f"{column} = ?")
            params.append(value)

        if conditions:
            sql += " WHERE " + " AND ".join(conditions)

    # ==============================
    #  GROUP BY
    # ==============================
    if aggregation and group_by:
        sql += f" GROUP BY {group_by}"

    # ==============================
    # ORDER BY
    # ==============================
    if aggregation:
        if order_by:
            sql += f" ORDER BY value {order_by}"
    else:
        if order_by:
            sql += f" ORDER BY {metric_column} {order_by}"

    print(f"[QueryService] Executing SQL: {sql}")
    print(f"[QueryService] Params: {params}")

    return execute_select_query(sql, params)
