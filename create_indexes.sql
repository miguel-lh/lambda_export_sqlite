-- ============================================================
-- SCRIPT DE CREACIÓN DE ÍNDICES PARA OPTIMIZACIÓN
-- ============================================================
--
-- Este script crea todos los índices necesarios para optimizar
-- las queries de exportación que usan is_removed = FALSE
--
-- IMPORTANTE:
-- - Ejecutar en la base de datos de PostgreSQL RDS
-- - Los índices se crean con CONCURRENTLY para no bloquear tablas
-- - Tiempo estimado de ejecución: 15-30 minutos
-- - Impacto: Reduce tiempo de queries de 3953ms a ~2200ms (44%)
--
-- ============================================================

-- Establecer configuración para creación de índices
SET maintenance_work_mem = '256MB';
SET max_parallel_maintenance_workers = 4;

\echo '============================================================'
\echo 'CREANDO ÍNDICES PARCIALES CON is_removed = FALSE'
\echo '============================================================'

-- ============================================================
-- CUSTOMERS
-- ============================================================
\echo ''
\echo 'Creando índice para CUSTOMERS...'
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_customer_parent_not_removed
ON customer_customer(parent_id)
WHERE parent_id IS NOT NULL AND is_removed = FALSE;

-- ============================================================
-- BANK ACCOUNTS
-- ============================================================
\echo 'Creando índice para BANK_ACCOUNTS...'
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_bank_accounts_not_removed
ON bank_accounts_bankaccounts(id)
WHERE is_removed = FALSE;

-- ============================================================
-- LIST PRICES
-- ============================================================
\echo 'Creando índice para LIST_PRICES...'
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_list_price_not_removed
ON list_price_pricelist(id)
WHERE is_removed = FALSE;

-- ============================================================
-- LIST PRICE DETAILS
-- ============================================================
\echo 'Creando índice para LIST_PRICE_DETAILS...'
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_list_price_detail_not_removed
ON list_price_pricelistdetail(price_list_id)
WHERE is_removed = FALSE;

-- ============================================================
-- CLIENT LIST PRICES (subconsultas)
-- ============================================================
\echo 'Creando índices para CLIENT_LIST_PRICES...'
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_customer_list_price_customer
ON customer_customer_list_price(customer_id);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_customer_list_price_pricelist
ON customer_customer_list_price(pricelist_id);

-- ============================================================
-- LOCATIONS
-- ============================================================
\echo 'Creando índice para LOCATIONS...'
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_location_parent_not_removed
ON location_location(parent_id)
WHERE parent_id IS NOT NULL AND is_removed = FALSE;

-- ============================================================
-- COBRANZAS
-- ============================================================
\echo 'Creando índice para COBRANZAS...'
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_cobranza_not_removed
ON cobranza_cobranza(customer_id)
WHERE is_removed = FALSE;

-- ============================================================
-- COBRANZA DETAILS
-- ============================================================
\echo 'Creando índice para COBRANZA_DETAILS...'
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_cobranza_detail_not_removed
ON cobranza_cobranzadetail(cobranza_id)
WHERE is_removed = FALSE;

-- ============================================================
-- PRODUCTS Y RELACIONES
-- ============================================================
\echo 'Creando índice para PRODUCTS...'
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_product_active_type
ON product_product(type, is_removed, delete_at)
WHERE is_removed = FALSE AND delete_at IS NULL;

\echo 'Creando índice para CATEGORIES...'
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_category_removed
ON category_category(id)
WHERE is_removed = FALSE AND delete_at IS NULL;

\echo 'Creando índice para BRANDS...'
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_brand_removed
ON brand_brand(id)
WHERE is_removed = FALSE AND delete_at IS NULL;

-- ============================================================
-- ACTUALIZAR ESTADÍSTICAS DE TABLAS
-- ============================================================
\echo ''
\echo '============================================================'
\echo 'ACTUALIZANDO ESTADÍSTICAS DE TABLAS (ANALYZE)'
\echo '============================================================'

ANALYZE customer_customer;
\echo '✓ customer_customer'

ANALYZE bank_accounts_bankaccounts;
\echo '✓ bank_accounts_bankaccounts'

ANALYZE list_price_pricelist;
\echo '✓ list_price_pricelist'

ANALYZE list_price_pricelistdetail;
\echo '✓ list_price_pricelistdetail'

ANALYZE customer_customer_list_price;
\echo '✓ customer_customer_list_price'

ANALYZE location_location;
\echo '✓ location_location'

ANALYZE cobranza_cobranza;
\echo '✓ cobranza_cobranza'

ANALYZE cobranza_cobranzadetail;
\echo '✓ cobranza_cobranzadetail'

ANALYZE product_product;
\echo '✓ product_product'

ANALYZE category_category;
\echo '✓ category_category'

ANALYZE brand_brand;
\echo '✓ brand_brand'

-- ============================================================
-- VERIFICAR ÍNDICES CREADOS
-- ============================================================
\echo ''
\echo '============================================================'
\echo 'ÍNDICES CREADOS EXITOSAMENTE'
\echo '============================================================'

SELECT
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) as index_size
FROM pg_indexes
JOIN pg_class ON pg_class.relname = indexname
WHERE schemaname = 'public'
  AND indexname LIKE 'idx_%not_removed%'
   OR indexname LIKE 'idx_customer_list_price%'
   OR indexname LIKE 'idx_product_active%'
   OR indexname LIKE 'idx_category_removed%'
   OR indexname LIKE 'idx_brand_removed%'
ORDER BY tablename, indexname;

\echo ''
\echo '============================================================'
\echo '✅ PROCESO COMPLETADO'
\echo '============================================================'
\echo ''
\echo 'Próximos pasos:'
\echo '1. Verificar los índices creados arriba'
\echo '2. Ejecutar prueba de la Lambda: python3 test_local.py'
\echo '3. Comparar tiempos: Debería ver reducción de ~3953ms → ~2200ms'
\echo ''
