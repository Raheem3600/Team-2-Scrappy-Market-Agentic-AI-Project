/* 
Script: 00_init_all.sql
Purpose: Single entry point for building the ScrappyMarket database.

Runs the full database setup in sequence:
- database creation
- schema
- indexes
- views
- seed data
- verification

Used for:
- local development
- Docker container initialization
*/

:r /db/00_create_database.sql
:r /db/00_reset.sql
:r /db/01_schema.sql
:r /db/02_indexes.sql
:r /db/03_views.sql
:r /db/04_seed_dimensions.sql
:r /db/05_seed_promotions.sql
:r /db/06_seed_sales.sql
-- :r /db/07_canonical_queries.sql
:r /db/99_verify.sql
GO
