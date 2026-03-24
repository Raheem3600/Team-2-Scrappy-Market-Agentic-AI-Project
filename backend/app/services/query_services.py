import pyodbc
from app.db import get_connection

ALLOWED_VIEWS = [
    "vw_sales_daily_store",
    "vw_sales_daily_product",
    "vw_promo_sales_fact",
    "vw_low_stock"
]

def execute_safe_query(view_name: str, filters: dict, limit: int = 100):

    if view_name not in ALLOWED_VIEWS:
        raise ValueError(f"View {view_name} not allowed")

    conn = get_connection()
    cursor = conn.cursor()

    query = f"SELECT TOP {limit} * FROM {view_name}"

    if filters:
        conditions = [f"{k} = '{v}'" for k, v in filters.items()]
        query += " WHERE " + " AND ".join(conditions)
    print(query)
    cursor.execute(query)

    columns = [col[0] for col in cursor.description]
    rows = cursor.fetchall()
    print(rows)
    results = [dict(zip(columns, row)) for row in rows]

    conn.close()
    return results