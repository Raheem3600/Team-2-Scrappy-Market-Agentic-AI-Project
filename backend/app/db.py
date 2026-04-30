import os
import pyodbc

def get_connection():
    server = os.getenv("DB_SERVER", "localhost,1433")
    database = os.getenv("DB_NAME", "ScrappyMarket")
    user = os.getenv("DB_USER", "sa")
    password = os.getenv("DB_PASSWORD", "IT7993!Scrappy")
    driver = os.getenv("ODBC_DRIVER", "ODBC Driver 18 for SQL Server")


    conn_str = (
        f"DRIVER={{{driver}}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"UID={user};"
        f"PWD={password};"
        "Encrypt=no;"
        "TrustServerCertificate=yes;"
    )

    return pyodbc.connect(conn_str)


