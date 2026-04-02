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
        "TotalSalesAmount", "TotalQuantitySold", "TransactionCount", "Region"
    },
    "vw_low_stock": {
        "StoreID", "StoreName", "ProductID", "ProductName",
        "OnHandQuantity", "ReorderPoint"
    },
    "vw_sales_enriched": {
        "SalesID", "DateKey", "StoreID", "StoreName", "Region", "City",
        "ProductID", "ProductName", "Category", "QuantitySold",
        "SalesAmount", "UnitPrice", "PromotionID", "PromotionName",
        "DiscountPct", "Channel", "WasOnPromotion"
    },
    "vw_promotions_enriched": {
        "PromotionID", "PromotionName", "DiscountPct",
        "StartDateKey", "EndDateKey"
    },
    "vw_sales_daily_product": {
        "DateKey", "ProductID", "ProductName", "Category",
        "TotalSalesAmount", "TotalQuantitySold"
    },
    "vw_promo_sales_fact": {
        "SalesID", "DateKey", "StoreID", "ProductID", "PromotionID",
        "QuantitySold", "SalesAmount", "UnitPrice"
    },
}


def execute_safe_query(view_name: str, filters: dict, limit: int):
    if view_name not in ALLOWED_VIEWS:
        raise ValueError(f"View '{view_name}' is not allowed.")

    valid_columns = VIEW_COLUMNS.get(view_name, set())

    for column in filters.keys():
        if column not in valid_columns:
            raise ValueError(f"Invalid filter column '{column}' for view '{view_name}'.")

    sql = f"SELECT TOP {int(limit)} * FROM dbo.{view_name}"
    params = []

    if filters:
        conditions = []
        for column, value in filters.items():
            conditions.append(f"{column} = ?")
            params.append(value)

        sql += " WHERE " + " AND ".join(conditions)

    return execute_select_query(sql, params)