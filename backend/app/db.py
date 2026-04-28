import os
import pyodbc

def get_connection():
    server = os.getenv("DB_SERVER", "localhost,1433")
    database = os.getenv("DB_NAME", "ScrappyMarket")


    conn_str = (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        f"SERVER={server};"
        f"DATABASE={database};"
        "UID=sa;"
        "PWD=IT7993!Scrappy;"
        "Encrypt=no;"
        "TrustServerCertificate=yes;"
    )

    return pyodbc.connect(conn_str)



