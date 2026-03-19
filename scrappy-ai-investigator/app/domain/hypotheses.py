HYPOTHESIS_REGISTRY = {
    "net_sales": [
        {
            "name": "store_sales_decline",
            "priority": 1,
            "description": "Sales decline across stores or regions"
        },
        {
            "name": "product_category_decline",
            "priority": 2,
            "description": "Specific products or categories causing decline"
        },
        {
            "name": "promotion_impact_change",
            "priority": 3,
            "description": "Changes in promotions affecting sales"
        },
        {
            "name": "inventory_stockout",
            "priority": 4,
            "description": "Low stock or stockouts reducing sales"
        }
    ],
    "orders": [
        {
            "name": "store_order_decline",
            "priority": 1,
            "description": "Drop in orders across stores"
        },
        {
            "name": "product_demand_drop",
            "priority": 2,
            "description": "Demand decrease for certain products"
        }
    ]
}