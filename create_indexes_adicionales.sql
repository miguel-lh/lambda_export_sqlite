-- ============================================================
-- ÍNDICES ADICIONALES PARA OPTIMIZACIÓN AVANZADA
-- ============================================================
--
-- Estos índices resuelven los problemas de queries lentas
-- identificados en el análisis de rendimiento
--
-- IMPORTANTE:
-- - Ejecutar DESPUÉS de create_indexes.sql
-- - Usar CONCURRENTLY para no bloquear tablas
-- - Impacto esperado: Reducción adicional de 4-5 segundos
--
-- ============================================================

SET maintenance_work_mem = '256MB';
SET max_parallel_maintenance_workers = 4;

\echo '============================================================'
\echo 'CREANDO ÍNDICES ADICIONALES PARA OPTIMIZACIÓN'
\echo '============================================================'

-- ============================================================
-- BANK ACCOUNTS - Para reemplazar subconsultas escalares
-- ============================================================
\echo ''
\echo 'Creando índices para BANK_ACCOUNTS JOINs...'

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_bank_accounts_bank_id
ON bank_accounts_bankaccounts(bank_id)
WHERE is_removed = FALSE;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_bank_accounts_accounting_id
ON bank_accounts_bankaccounts(accounting_account_id)
WHERE is_removed = FALSE;

-- ============================================================
-- CUSTOMER - Índice compuesto para JOINs más eficientes
-- ============================================================
\echo 'Creando índice compuesto para CUSTOMER...'

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_customer_id_parent
ON customer_customer(id, parent_id)
WHERE is_removed = FALSE;

-- ============================================================
-- LOCATIONS - Índice compuesto para mejorar filtrado
-- ============================================================
\echo 'Creando índice compuesto para LOCATIONS...'

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_location_parent_removed_composite
ON location_location(parent_id, is_removed)
WHERE is_removed = FALSE;

-- También crear índices para las foreign keys si se usan en filtros
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_location_zone
ON location_location(zone_id)
WHERE is_removed = FALSE;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_location_category
ON location_location(category_id)
WHERE is_removed = FALSE;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_location_type
ON location_location(type_location_id)
WHERE is_removed = FALSE;

-- ============================================================
-- PRODUCTS - Índices para las foreign keys en JOINs
-- ============================================================
\echo 'Creando índices para PRODUCTS foreign keys...'

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_product_category
ON product_product(category_id)
WHERE is_removed = FALSE AND delete_at IS NULL;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_product_brand
ON product_product(brand_id)
WHERE is_removed = FALSE AND delete_at IS NULL;

-- ============================================================
-- ACTUALIZAR ESTADÍSTICAS
-- ============================================================
\echo ''
\echo 'Actualizando estadísticas...'

ANALYZE bank_accounts_bankaccounts;
ANALYZE customer_customer;
ANALYZE location_location;
ANALYZE product_product;

\echo ''
\echo '============================================================'
\echo '✅ ÍNDICES ADICIONALES CREADOS'
\echo '============================================================'
\echo ''
\echo 'Próximos pasos:'
\echo '1. Actualizar las queries en postgres_repository.py'
\echo '2. Ejecutar test: python3 test_local.py'
\echo '3. Tiempo esperado: ~1-2 segundos (vs actual 5.2s)'
\echo ''
