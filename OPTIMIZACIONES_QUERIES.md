# 🚀 Optimizaciones de Queries PostgreSQL

## 📊 Resumen del Análisis

**Tiempo actual:** 5.2 segundos
**Tiempo objetivo:** 1-2 segundos
**Reducción esperada:** ~60-70%

---

## 🔧 Cambios Necesarios en `postgres_repository.py`

### 1. 🚨 CRÍTICO: BANK_ACCOUNTS (Línea 384)

**Problema:** Subconsultas escalares en SELECT ejecutan 2 queries por fila
**Tiempo actual:** 408ms para 2 registros
**Tiempo esperado:** ~30ms

**ANTES:**
```python
query = """
    SELECT
        ba.id,
        ba.name,
        (SELECT b.name FROM bank_accounts_bank b WHERE b.id = ba.bank_id) as bank_name,
        ba.number,
        (SELECT baa.name FROM bank_accounts_accountingaccount baa WHERE baa.id = ba.accounting_account_id) as accounting_account_name
    FROM bank_accounts_bankaccounts as ba
    WHERE ba.is_removed = FALSE
    ORDER BY ba.id
    LIMIT 100
"""
```

**DESPUÉS:**
```python
query = """
    SELECT
        ba.id,
        ba.name,
        b.name as bank_name,
        ba.number,
        baa.name as accounting_account_name
    FROM bank_accounts_bankaccounts ba
    LEFT JOIN bank_accounts_bank b ON ba.bank_id = b.id
    LEFT JOIN bank_accounts_accountingaccount baa ON ba.accounting_account_id = baa.id
    WHERE ba.is_removed = FALSE
    ORDER BY ba.id
    LIMIT 100
"""
```

---

### 2. 🚨 CRÍTICO: CLIENT_LIST_PRICES (Línea 599)

**Problema:** Subconsulta IN genera lista grande de IDs
**Tiempo actual:** 2840ms execute
**Tiempo esperado:** ~300ms

**ANTES:**
```python
query = """
    SELECT
        id,
        customer_id as id_client,
        pricelist_id as id_list_price
    FROM customer_customer_list_price
    WHERE customer_id IN (
        SELECT id
        FROM customer_customer
        WHERE parent_id = %s
    )
    ORDER BY id
"""
```

**DESPUÉS:**
```python
query = """
    SELECT
        clp.id,
        clp.customer_id as id_client,
        clp.pricelist_id as id_list_price
    FROM customer_customer_list_price clp
    INNER JOIN customer_customer cc ON clp.customer_id = cc.id
    WHERE cc.parent_id = %s
      AND cc.is_removed = FALSE
    ORDER BY clp.id
"""
```

---

### 3. 🚨 CRÍTICO: LIST_PRICES (Línea 453)

**Problema:** Subconsulta compleja con DISTINCT + JOIN
**Tiempo actual:** 1828ms execute
**Tiempo esperado:** ~200ms

**ANTES:**
```python
query = """
    SELECT
        l.id,
        l.name,
        l.max,
        l.min,
        l.customer_sync_id as customer_sync
    FROM list_price_pricelist as l
    WHERE l.id IN (
        SELECT DISTINCT clp.pricelist_id
        FROM customer_customer_list_price clp
        INNER JOIN customer_customer cc ON clp.customer_id = cc.id
        WHERE cc.parent_id = %s
    )
    AND l.is_removed = FALSE
    ORDER BY l.id
"""
```

**DESPUÉS:**
```python
query = """
    SELECT DISTINCT
        l.id,
        l.name,
        l.max,
        l.min,
        l.customer_sync_id as customer_sync
    FROM list_price_pricelist l
    INNER JOIN customer_customer_list_price clp ON l.id = clp.pricelist_id
    INNER JOIN customer_customer cc ON clp.customer_id = cc.id
    WHERE cc.parent_id = %s
      AND l.is_removed = FALSE
      AND cc.is_removed = FALSE
    ORDER BY l.id
"""
```

---

### 4. 🚨 CRÍTICO: LOCATIONS (Línea 668)

**Problema:** Conversión geofence::text + posibles triggers
**Tiempo actual:** 1503ms para 14 registros
**Tiempo esperado:** ~50ms

**Investigación necesaria:**
```sql
-- Ejecutar en PostgreSQL para diagnóstico:

-- 1. Verificar triggers
SELECT tgname, tgtype, tgfoid::regproc
FROM pg_trigger
WHERE tgrelid = 'location_location'::regclass;

-- 2. Verificar políticas RLS
SELECT * FROM pg_policies WHERE tablename = 'location_location';

-- 3. Verificar tamaño de geofence
SELECT
    avg(pg_column_size(geofence)) as avg_size,
    max(pg_column_size(geofence)) as max_size
FROM location_location
WHERE parent_id = 1843;
```

**Solución temporal (si no necesitas geofence):**
```python
# Eliminar la línea:
# geofence::text as geofence,

# Y en el mapeo de Location, quitar:
# geofence=row.get('geofence'),
```

---

### 5. ⚠️ RECOMENDACIÓN: CUSTOMERS (Línea 162)

**Problema:** Campo geofence grande causa fetch lento
**Tiempo actual:** 3295ms fetch (84% del tiempo)
**Impacto:** Bajo si necesitas el campo

**Opciones:**
1. Si NO necesitas geofence: Elimínalo completamente
2. Si lo necesitas: Déjalo como está (ya está optimizado con ::text)

---

### 6. ⚠️ RECOMENDACIÓN: PRODUCTS (Línea 296)

**Problema:** Fetch lento por volumen de datos
**Tiempo actual:** 2975ms fetch (84.5% del tiempo)
**Estado:** Ya está bien optimizado con LEFT JOINs

**Posible mejora adicional:**
```python
# Si no necesitas description (que puede ser larga), quítala:
# description,  # <- comentar esta línea
```

---

## 📋 Plan de Implementación

### Fase 1: Índices (Ejecutar primero)
```bash
# 1. Ejecutar índices adicionales
psql -h <RDS_ENDPOINT> -U <USER> -d <DB> -f create_indexes_adicionales.sql

# 2. Verificar índices creados
psql -h <RDS_ENDPOINT> -U <USER> -d <DB> -c "
SELECT tablename, indexname, pg_size_pretty(pg_relation_size(indexname::regclass))
FROM pg_indexes
WHERE schemaname = 'public'
  AND indexname LIKE 'idx_%'
ORDER BY tablename, indexname;
"
```

### Fase 2: Cambios en Código (Después de índices)

**Prioridad ALTA (hacer primero):**
1. ✅ Reescribir `get_bank_accounts_by_tenant()` - línea 377
2. ✅ Reescribir `get_client_list_prices_by_tenant()` - línea 593
3. ✅ Reescribir `get_list_prices_by_tenant()` - línea 447
4. ⚠️ Investigar `get_locations_by_tenant()` - línea 661

**Prioridad MEDIA:**
5. Considerar eliminar geofence de CUSTOMERS si no se usa
6. Considerar eliminar description de PRODUCTS si no se usa

### Fase 3: Testing
```bash
# Ejecutar test local
python3 test_local.py

# Comparar resultados:
# - Tiempo esperado: 1-2 segundos (vs actual 5.2s)
# - Las queries problemáticas deberían reducirse 70-80%
```

---

## 📊 Impacto Esperado por Query

| Query | Tiempo Actual | Tiempo Esperado | Reducción |
|-------|--------------|----------------|-----------|
| bank_accounts | 408ms | ~30ms | 93% ⭐⭐⭐ |
| client_list_prices | 2878ms | ~300ms | 90% ⭐⭐⭐ |
| list_prices | 1835ms | ~200ms | 89% ⭐⭐⭐ |
| locations | 2341ms | ~100ms | 96% ⭐⭐⭐ |
| customers | 3920ms | ~2500ms | 36% ⭐ |
| products | 3520ms | ~2800ms | 20% ⭐ |
| **TOTAL** | **5205ms** | **~1500ms** | **71%** |

---

## 🔍 Comandos de Diagnóstico

### Verificar uso de índices
```sql
EXPLAIN ANALYZE
SELECT ba.id, ba.name, b.name as bank_name
FROM bank_accounts_bankaccounts ba
LEFT JOIN bank_accounts_bank b ON ba.bank_id = b.id
WHERE ba.is_removed = FALSE
LIMIT 100;
```

### Verificar triggers en locations
```sql
SELECT
    tgname as trigger_name,
    tgtype,
    tgfoid::regproc as function_name,
    tgenabled
FROM pg_trigger
WHERE tgrelid = 'location_location'::regclass
  AND tgisinternal = false;
```

### Verificar tamaño de geofence
```sql
SELECT
    COUNT(*) as records,
    pg_size_pretty(avg(pg_column_size(geofence))::bigint) as avg_geofence_size,
    pg_size_pretty(max(pg_column_size(geofence))::bigint) as max_geofence_size
FROM customer_customer
WHERE parent_id = 1843;
```

---

## ✅ Checklist de Implementación

- [ ] Ejecutar `create_indexes_adicionales.sql` en RDS
- [ ] Verificar índices creados
- [ ] Investigar triggers/RLS en locations
- [ ] Actualizar query de `get_bank_accounts_by_tenant()`
- [ ] Actualizar query de `get_client_list_prices_by_tenant()`
- [ ] Actualizar query de `get_list_prices_by_tenant()`
- [ ] Ejecutar test local y comparar tiempos
- [ ] Decidir sobre geofence en customers/locations
- [ ] Deploy a Lambda y prueba en staging
- [ ] Monitorear métricas en CloudWatch

---

## 🎯 Objetivo Final

**Meta:** Reducir tiempo de exportación de **5.2s → 1.5s** (71% de mejora)

**Beneficio:**
- Mejor experiencia de usuario
- Menor costo de Lambda (menos tiempo de ejecución)
- Mayor capacidad de concurrencia
- Menor carga en RDS PostgreSQL
