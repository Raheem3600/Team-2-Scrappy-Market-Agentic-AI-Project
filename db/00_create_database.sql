/* =========================
   Create Database: ScrappyMarket
========================= */

-- Create DB if it doesn't exist
IF DB_ID('ScrappyMarket') IS NULL
BEGIN
    CREATE DATABASE ScrappyMarket;
END
GO

-- Use it
USE ScrappyMarket;
GO

-- Optional: basic sanity check
SELECT DB_NAME() AS CurrentDatabase;
GO