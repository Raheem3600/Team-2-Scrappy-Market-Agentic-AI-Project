LINEAGE_REGISTRY = {
    "store_sales_decline": {
        "view": "vw_sales_daily_store",
        "group_by": ["Date", "Region"],
        "metrics": ["SalesAmount", "UnitsSold"]
    },
    "product_category_decline": {
        "view": "vw_sales_daily_product",
        "group_by": ["Date", "Category"],
        "metrics": ["SalesAmount", "UnitsSold"]
    },
    "promotion_impact_change": {
        "view": "vw_promo_sales_fact",
        "group_by": ["Date", "PromotionName"],
        "metrics": ["SalesAmount", "UnitsSold"]
    },
    "inventory_stockout": {
        "view": "vw_low_stock",
        "group_by": ["Date", "StoreID", "ProductID"],
        "metrics": ["OnHandQuantity", "IsBelowReorderPoint"]
    },
    "store_order_decline": {
        "view": "vw_sales_daily_store",
        "group_by": ["Date", "Region"],
        "metrics": ["UnitsSold"]  # orders proxy
    },

    "product_demand_drop": {
        "view": "vw_sales_daily_product",
        "group_by": ["Date", "Category"],
        "metrics": ["UnitsSold"]
    },
}