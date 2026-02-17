/* 99_verify.sql */
USE ScrappyMarket;
GO

SELECT name FROM sys.tables ORDER BY name;
SELECT name FROM sys.views  ORDER BY name;

-- Check FK existence quickly
SELECT
    fk.name AS FK_Name,
    OBJECT_NAME(fk.parent_object_id) AS ChildTable,
    OBJECT_NAME(fk.referenced_object_id) AS ParentTable
FROM sys.foreign_keys fk
ORDER BY ChildTable, ParentTable;
GO