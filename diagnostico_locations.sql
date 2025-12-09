-- ============================================================
-- SCRIPT DE DIAGNÓSTICO PARA LOCATIONS
-- ============================================================
--
-- Esta query toma 2.3 segundos para solo 14 registros (171ms/registro)
-- Este script ayuda a identificar la causa raíz del problema
--
-- Ejecutar con:
-- psql -h <RDS_ENDPOINT> -U <USER> -d <DB> -f diagnostico_locations.sql
-- ============================================================

\echo ''
\echo '============================================================'
\echo 'DIAGNÓSTICO DE RENDIMIENTO: location_location'
\echo '============================================================'
\echo ''

-- ============================================================
-- 1. VERIFICAR TRIGGERS
-- ============================================================
\echo '1. Verificando triggers activos en location_location:'
\echo '   (Los triggers pueden ejecutar código adicional en cada SELECT)'
\echo ''

SELECT
    tgname as "Trigger Name",
    CASE
        WHEN tgtype::int & 1 = 1 THEN 'ROW'
        ELSE 'STATEMENT'
    END as "Level",
    CASE
        WHEN tgtype::int & 2 = 2 THEN 'BEFORE'
        WHEN tgtype::int & 64 = 64 THEN 'INSTEAD OF'
        ELSE 'AFTER'
    END as "Timing",
    CASE
        WHEN tgtype::int & 4 = 4 THEN 'INSERT'
        WHEN tgtype::int & 8 = 8 THEN 'DELETE'
        WHEN tgtype::int & 16 = 16 THEN 'UPDATE'
        ELSE 'OTHER'
    END as "Event",
    tgfoid::regproc as "Function",
    CASE tgenabled
        WHEN 'O' THEN 'ENABLED'
        WHEN 'D' THEN 'DISABLED'
        WHEN 'R' THEN 'REPLICA'
        WHEN 'A' THEN 'ALWAYS'
    END as "Status"
FROM pg_trigger
WHERE tgrelid = 'location_location'::regclass
  AND tgisinternal = false
ORDER BY tgname;

\echo ''
\echo '   ⚠️  Si hay triggers habilitados, pueden estar ralentizando los SELECT'
\echo ''

-- ============================================================
-- 2. VERIFICAR ROW-LEVEL SECURITY (RLS)
-- ============================================================
\echo '2. Verificando políticas de Row-Level Security (RLS):'
\echo '   (RLS agrega filtros adicionales a cada query)'
\echo ''

-- Verificar si RLS está habilitado
SELECT
    relname as "Table",
    relrowsecurity as "RLS Enabled",
    relforcerowsecurity as "Force RLS"
FROM pg_class
WHERE relname = 'location_location';

\echo ''

-- Verificar políticas RLS activas
SELECT
    schemaname as "Schema",
    tablename as "Table",
    policyname as "Policy Name",
    permissive as "Permissive",
    roles as "Roles",
    cmd as "Command",
    qual as "Using Expression",
    with_check as "With Check Expression"
FROM pg_policies
WHERE tablename = 'location_location';

\echo ''
\echo '   ⚠️  Si RLS está habilitado, cada SELECT ejecuta las políticas definidas'
\echo ''

-- ============================================================
-- 3. VERIFICAR TAMAÑO DEL CAMPO GEOFENCE
-- ============================================================
\echo '3. Analizando tamaño del campo geofence (JSONB):'
\echo '   (Conversión a texto puede ser costosa si el campo es grande)'
\echo ''

SELECT
    COUNT(*) as "Total Records",
    pg_size_pretty(AVG(pg_column_size(geofence))::bigint) as "Avg Geofence Size",
    pg_size_pretty(MAX(pg_column_size(geofence))::bigint) as "Max Geofence Size",
    pg_size_pretty(SUM(pg_column_size(geofence))::bigint) as "Total Geofence Size",
    COUNT(CASE WHEN geofence IS NOT NULL THEN 1 END) as "Non-NULL Geofences",
    COUNT(CASE WHEN pg_column_size(geofence) > 1024 THEN 1 END) as "Geofences > 1KB"
FROM location_location
WHERE parent_id = 1843;

\echo ''
\echo '   ⚠️  Si el promedio es > 1KB, considerar eliminar geofence de la query'
\echo ''

-- ============================================================
-- 4. PROBAR QUERY SIN GEOFENCE
-- ============================================================
\echo '4. Comparando rendimiento CON vs SIN geofence:'
\echo ''

-- Query CON geofence::text
\echo '   a) Query CON geofence::text...'
\timing on

EXPLAIN ANALYZE
SELECT
    id, slug, name, tel, email, code, sequence, format,
    zone_id, "using", category_id, type_location_id,
    street, ext_number, int_number, suburb, code_postal,
    city, state, country, lat, lng,
    geofence::text as geofence,  -- ← Esta conversión es costosa
    sequence_times_from_1, sequence_times_up_to_1,
    sequence_times_from_2, sequence_times_up_to_2,
    sequence_times_from_3, sequence_times_up_to_3,
    is_pay_sun, is_pay_mon, is_pay_tues, is_pay_wed,
    is_pay_thurs, is_pay_fri, is_pay_sat,
    seller, checked
FROM location_location
WHERE parent_id = 1843 AND is_removed = FALSE
ORDER BY id;

\echo ''
\echo '   b) Query SIN geofence...'

EXPLAIN ANALYZE
SELECT
    id, slug, name, tel, email, code, sequence, format,
    zone_id, "using", category_id, type_location_id,
    street, ext_number, int_number, suburb, code_postal,
    city, state, country, lat, lng,
    -- geofence eliminado
    sequence_times_from_1, sequence_times_up_to_1,
    sequence_times_from_2, sequence_times_up_to_2,
    sequence_times_from_3, sequence_times_up_to_3,
    is_pay_sun, is_pay_mon, is_pay_tues, is_pay_wed,
    is_pay_thurs, is_pay_fri, is_pay_sat,
    seller, checked
FROM location_location
WHERE parent_id = 1843 AND is_removed = FALSE
ORDER BY id;

\timing off

\echo ''
\echo '   ⚠️  Comparar "Execution Time" de ambas queries'
\echo '   ⚠️  Si la diferencia es significativa, eliminar geofence del código Python'
\echo ''

-- ============================================================
-- 5. VERIFICAR ÍNDICES EXISTENTES
-- ============================================================
\echo '5. Índices disponibles en location_location:'
\echo ''

SELECT
    indexname as "Index Name",
    indexdef as "Definition",
    pg_size_pretty(pg_relation_size(indexname::regclass)) as "Size"
FROM pg_indexes
WHERE tablename = 'location_location'
  AND schemaname = 'public'
ORDER BY indexname;

\echo ''
\echo '   ✓ Verificar que existe: idx_location_parent_not_removed'
\echo ''

-- ============================================================
-- 6. ESTADÍSTICAS DE LA TABLA
-- ============================================================
\echo '6. Estadísticas de la tabla:'
\echo ''

SELECT
    relname as "Table",
    n_live_tup as "Live Rows",
    n_dead_tup as "Dead Rows",
    last_vacuum,
    last_autovacuum,
    last_analyze,
    last_autoanalyze
FROM pg_stat_user_tables
WHERE relname = 'location_location';

\echo ''
\echo '   ⚠️  Si last_analyze es NULL o muy antiguo, ejecutar: ANALYZE location_location;'
\echo ''

-- ============================================================
-- RESUMEN Y RECOMENDACIONES
-- ============================================================
\echo '============================================================'
\echo 'RESUMEN DE DIAGNÓSTICO COMPLETADO'
\echo '============================================================'
\echo ''
\echo 'Acciones recomendadas basadas en los resultados:'
\echo ''
\echo '1. Si hay TRIGGERS habilitados:'
\echo '   → Deshabilitar triggers innecesarios para SELECT'
\echo '   → O considerar usar una vista materializada'
\echo ''
\echo '2. Si RLS está habilitado:'
\echo '   → Evaluar si es necesario para esta tabla'
\echo '   → Usar SECURITY DEFINER function si es posible'
\echo ''
\echo '3. Si geofence es grande (> 1KB promedio):'
\echo '   → Eliminar geofence::text de la query'
\echo '   → Actualizar postgres_repository.py línea 692'
\echo ''
\echo '4. Si los índices no existen:'
\echo '   → Ejecutar create_indexes_adicionales.sql'
\echo ''
\echo '5. Si last_analyze es antiguo:'
\echo '   → ANALYZE location_location;'
\echo ''
\echo '============================================================'
\echo ''
