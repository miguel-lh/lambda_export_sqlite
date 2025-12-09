# Guía Rápida: Crear Índices en RDS PostgreSQL

## 🎯 Objetivo

Crear índices optimizados en tu base de datos RDS para reducir el tiempo de exportación de **3953ms → ~2200ms** (44% más rápido).

---

## ⚡ Opción 1: Script Automatizado (Recomendado)

### Paso 1: Conectarse a RDS

```bash
psql -h snapshots081020232.crgij3iw0xe0.us-west-2.rds.amazonaws.com \
     -U af_master \
     -d production \
     -p 5432
```

### Paso 2: Ejecutar el Script

Una vez conectado a PostgreSQL:

```sql
\i create_indexes.sql
```

O desde la terminal sin conectarte primero:

```bash
psql -h snapshots081020232.crgij3iw0xe0.us-west-2.rds.amazonaws.com \
     -U af_master \
     -d production \
     -p 5432 \
     -f create_indexes.sql
```

**Tiempo estimado:** 15-30 minutos

---

## 📋 Opción 2: Ejecutar Comandos Manualmente

Si prefieres ejecutar los comandos uno por uno, copia y pega desde `create_indexes.sql` o desde `AWS_OPTIMIZATION.md` (líneas 169-242).

---

## ✅ Verificar que los Índices se Crearon

```sql
-- Ver todos los índices creados
SELECT
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) as size
FROM pg_indexes
JOIN pg_class ON pg_class.relname = indexname
WHERE schemaname = 'public'
  AND (
    indexname LIKE 'idx_%not_removed%'
    OR indexname LIKE 'idx_customer_list_price%'
    OR indexname LIKE 'idx_product_active%'
    OR indexname LIKE 'idx_category_removed%'
    OR indexname LIKE 'idx_brand_removed%'
  )
ORDER BY tablename, indexname;
```

Deberías ver **13 índices** creados.

---

## 🧪 Probar la Mejora

Después de crear los índices, ejecuta la prueba local:

```bash
cd /home/mlg/Documents/lambda_export_sqlite
python3 test_local.py
```

### Resultados Esperados

**ANTES (sin índices):**
```
⏱️  Tiempo total de ejecución: 3953 ms
```

**DESPUÉS (con índices):**
```
⏱️  Tiempo total de ejecución: ~2200 ms
```

**Mejora:** ~1750ms ahorrados (44% más rápido) ⚡

---

## 📊 Índices Creados

| Índice | Tabla | Impacto |
|--------|-------|---------|
| idx_customer_parent_not_removed | customer_customer | Alto |
| idx_bank_accounts_not_removed | bank_accounts_bankaccounts | Alto |
| idx_list_price_not_removed | list_price_pricelist | Alto |
| idx_list_price_detail_not_removed | list_price_pricelistdetail | Alto |
| idx_customer_list_price_customer | customer_customer_list_price | Medio |
| idx_customer_list_price_pricelist | customer_customer_list_price | Medio |
| idx_location_parent_not_removed | location_location | Alto |
| idx_cobranza_not_removed | cobranza_cobranza | Medio |
| idx_cobranza_detail_not_removed | cobranza_cobranzadetail | Medio |
| idx_product_active_type | product_product | Medio |
| idx_category_removed | category_category | Bajo |
| idx_brand_removed | brand_brand | Bajo |

---

## ❓ FAQ

### ¿Por qué usar CONCURRENTLY?

`CREATE INDEX CONCURRENTLY` permite crear índices sin bloquear la tabla. La base de datos sigue funcionando normalmente durante la creación.

### ¿Cuánto espacio ocupan los índices?

Aproximadamente 50-200MB dependiendo del tamaño de tus tablas.

### ¿Puedo eliminar un índice si ya no lo necesito?

Sí:
```sql
DROP INDEX CONCURRENTLY idx_customer_parent_not_removed;
```

### ¿Los índices se mantienen automáticamente?

Sí, PostgreSQL los actualiza automáticamente cuando se insertan/actualizan datos.

---

## 🚨 Troubleshooting

### Error: "could not create unique index"
- Los índices parciales no necesitan ser únicos, verifica que no estés usando UNIQUE

### Error: "relation already exists"
- El índice ya existe. Usa `DROP INDEX CONCURRENTLY nombre_indice` primero o ignora el error

### La creación tarda mucho (>1 hora)
- Normal si tienes millones de registros
- Verifica el progreso con:
  ```sql
  SELECT * FROM pg_stat_progress_create_index;
  ```

---

## 📚 Más Información

- Ver guía completa: `AWS_OPTIMIZATION.md`
- Queries optimizadas: `src/infrastructure/postgres_repository.py`
