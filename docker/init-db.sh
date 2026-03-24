#!/bin/bash

echo "Waiting for SQL Server to start..."

for i in {1..30}
do
  /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P "$MSSQL_SA_PASSWORD" -C -Q "SELECT 1" > /dev/null 2>&1
  if [ $? -eq 0 ]
  then
    echo "SQL Server is ready."
    break
  fi
  echo "Still waiting..."
  sleep 2
done

echo "Running database initialization script..."
/opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P "$MSSQL_SA_PASSWORD" -C -i /db/00_init_all.sql

echo "Database initialization complete."