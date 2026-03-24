import pyodbc

conn = pyodbc.connect(
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=127.0.0.1,1433;"
    "DATABASE=ScrappyMarket;"
    "UID=sa;"
    "PWD=IT7993!Scrappy;"
    "Encrypt=no;"
    "TrustServerCertificate=yes;"
)

print("CONNECTED ✅")