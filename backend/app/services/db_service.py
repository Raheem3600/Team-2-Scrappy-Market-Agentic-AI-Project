from app.db import get_connection


def get_views():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name
        FROM sys.views
        ORDER BY name
    """)

    rows = cursor.fetchall()
    conn.close()

    return [row[0] for row in rows]


def get_columns(view_name: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COLUMN_NAME
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = ?
        ORDER BY ORDINAL_POSITION
    """, view_name)

    rows = cursor.fetchall()
    conn.close()

    return [row[0] for row in rows]


def execute_select_query(sql: str, params=None):
    conn = get_connection()
    cursor = conn.cursor()

    if params:
        cursor.execute(sql, params)
    else:
        cursor.execute(sql)

    columns = [col[0] for col in cursor.description]
    rows = cursor.fetchall()

    results = [dict(zip(columns, row)) for row in rows]

    cursor.close()
    conn.close()

    return results