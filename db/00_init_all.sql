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

:r .\00_create_database.sql
:r .\00_reset.sql
:r .\01_schema.sql
:r .\02_indexes.sql
:r .\03_views.sql
:r .\04_seed_dimensions.sql
:r .\05_seed_promotions.sql
:r .\06_seed_sales.sql
-- :r .\07_canonical_queries.sql   -- optional (read-only queries)
:r .\99_verify.sql
GO