# Optimizaciones de Infraestructura AWS

Este documento describe las optimizaciones de infraestructura en AWS para mejorar el rendimiento de la Lambda de exportación.

## 🎯 Estado Actual

```
Lambda → Internet → RDS PostgreSQL
Latencia estimada: Alta (posible NAT Gateway)
```

---

## ✅ Optimizaciones Recomendadas

### 1. **Lambda y RDS en la Misma VPC** (Crítico)

**Beneficio:** Reduce latencia de ~100ms a ~1-5ms

#### Pasos:

1. **Configura tu Lambda dentro de la VPC:**
   ```yaml
   # template.yaml (SAM)
   Resources:
     ExportFunction:
       Type: AWS::Serverless::Function
       Properties:
         VpcConfig:
           SecurityGroupIds:
             - !Ref LambdaSecurityGroup
           SubnetIds:
             - !Ref PrivateSubnet1
             - !Ref PrivateSubnet2
   ```

2. **Crea Security Group para Lambda:**
   ```bash
   # Permitir tráfico saliente a RDS en puerto 5432
   aws ec2 authorize-security-group-egress \
     --group-id sg-lambda-xxx \
     --protocol tcp \
     --port 5432 \
     --source-group sg-rds-xxx
   ```

3. **Actualiza Security Group de RDS:**
   ```bash
   # Permitir tráfico entrante desde Lambda
   aws ec2 authorize-security-group-ingress \
     --group-id sg-rds-xxx \
     --protocol tcp \
     --port 5432 \
     --source-group sg-lambda-xxx
   ```

**⚠️ Importante:** Lambda en VPC necesita acceso a Internet para otros servicios:
- Opción A: NAT Gateway (costo: ~$32/mes)
- Opción B: VPC Endpoints para servicios AWS (más barato)

---

### 2. **RDS Proxy** (Altamente Recomendado)

**Beneficio:**
- Reutiliza conexiones (ahorra ~100-500ms por invocación)
- Reduce carga en RDS
- Maneja mejor los picos de tráfico

#### Pasos:

1. **Crear RDS Proxy:**
   ```bash
   aws rds create-db-proxy \
     --db-proxy-name export-lambda-proxy \
     --engine-family POSTGRESQL \
     --auth [{
       "AuthScheme": "SECRETS",
       "SecretArn": "arn:aws:secretsmanager:region:account:secret:db-secret",
       "IAMAuth": "DISABLED"
     }] \
     --role-arn arn:aws:iam::account:role/RDSProxyRole \
     --vpc-subnet-ids subnet-xxx subnet-yyy \
     --require-tls false
   ```

2. **Registrar Target (tu RDS):**
   ```bash
   aws rds register-db-proxy-targets \
     --db-proxy-name export-lambda-proxy \
     --db-instance-identifiers snapshots081020232
   ```

3. **Actualizar variable de entorno en Lambda:**
   ```bash
   # Cambiar de:
   POSTGRES_HOST=snapshots081020232.crgij3iw0xe0.us-west-2.rds.amazonaws.com
   # A:
   POSTGRES_HOST=export-lambda-proxy.proxy-xxx.us-west-2.rds.amazonaws.com
   ```

**Costo estimado:** ~$0.015/hora (~$11/mes)

---

### 3. **Evitar NAT Gateway** (Ahorra $$$ y latencia)

Si tu Lambda está en VPC y necesita acceso a Internet:

#### Opción A: VPC Endpoints (Recomendado)

```bash
# Endpoint para Secrets Manager (si usas secretos)
aws ec2 create-vpc-endpoint \
  --vpc-id vpc-xxx \
  --service-name com.amazonaws.us-west-2.secretsmanager \
  --subnet-ids subnet-xxx subnet-yyy

# Endpoint para S3 (si guardas archivos)
aws ec2 create-vpc-endpoint \
  --vpc-id vpc-xxx \
  --service-name com.amazonaws.us-west-2.s3 \
  --route-table-ids rtb-xxx
```

**Costo:** Gateway endpoints (S3, DynamoDB) = GRATIS
**Costo:** Interface endpoints = ~$7.50/mes cada uno

#### Opción B: NAT Gateway (Más caro)

Solo si necesitas acceso general a Internet.

**Costo:** ~$32/mes + $0.045/GB transferido

---

### 4. **Optimizar Configuración de RDS**

#### A. Parameter Group Personalizado

```sql
-- Crear parameter group
aws rds create-db-parameter-group \
  --db-parameter-group-name optimized-postgres \
  --db-parameter-group-family postgres15 \
  --description "Optimized for read-heavy workloads"

-- Modificar parámetros
aws rds modify-db-parameter-group \
  --db-parameter-group-name optimized-postgres \
  --parameters "ParameterName=shared_buffers,ParameterValue='{DBInstanceClassMemory/4}',ApplyMethod=pending-reboot" \
               "ParameterName=effective_cache_size,ParameterValue='{DBInstanceClassMemory*3/4}',ApplyMethod=immediate" \
               "ParameterName=work_mem,ParameterValue=16MB,ApplyMethod=immediate" \
               "ParameterName=maintenance_work_mem,ParameterValue=256MB,ApplyMethod=immediate"
```

#### B. Crear Índices (¡MUY IMPORTANTE!)

**CRÍTICO:** Estas queries usan `is_removed = FALSE`, los índices deben incluir este filtro.

```sql
-- Conectarse a RDS y ejecutar:

-- ============================================================
-- ÍNDICES PARCIALES CON is_removed = FALSE (CRÍTICO)
-- ============================================================

-- Customers (filtra por parent_id AND is_removed = FALSE)
CREATE INDEX CONCURRENTLY idx_customer_parent_not_removed
ON customer_customer(parent_id)
WHERE parent_id IS NOT NULL AND is_removed = FALSE;

-- Bank Accounts (filtra por is_removed = FALSE)
CREATE INDEX CONCURRENTLY idx_bank_accounts_not_removed
ON bank_accounts_bankaccounts(id)
WHERE is_removed = FALSE;

-- List Prices (filtra por id AND is_removed = FALSE)
CREATE INDEX CONCURRENTLY idx_list_price_not_removed
ON list_price_pricelist(id)
WHERE is_removed = FALSE;

-- List Price Details (filtra por price_list_id AND is_removed = FALSE)
CREATE INDEX CONCURRENTLY idx_list_price_detail_not_removed
ON list_price_pricelistdetail(price_list_id)
WHERE is_removed = FALSE;

-- Client List Prices (para subconsultas)
CREATE INDEX CONCURRENTLY idx_customer_list_price_customer
ON customer_customer_list_price(customer_id);

CREATE INDEX CONCURRENTLY idx_customer_list_price_pricelist
ON customer_customer_list_price(pricelist_id);

-- Locations (filtra por parent_id AND is_removed = FALSE)
CREATE INDEX CONCURRENTLY idx_location_parent_not_removed
ON location_location(parent_id)
WHERE parent_id IS NOT NULL AND is_removed = FALSE;

-- Cobranzas (filtra por customer_id AND is_removed = FALSE)
CREATE INDEX CONCURRENTLY idx_cobranza_not_removed
ON cobranza_cobranza(customer_id)
WHERE is_removed = FALSE;

-- Cobranza Details (filtra por cobranza_id AND is_removed = FALSE)
CREATE INDEX CONCURRENTLY idx_cobranza_detail_not_removed
ON cobranza_cobranzadetail(cobranza_id)
WHERE is_removed = FALSE;

-- ============================================================
-- ÍNDICES PARA PRODUCTS Y RELACIONES
-- ============================================================

-- Products (usa LEFT JOIN con condiciones is_removed)
CREATE INDEX CONCURRENTLY idx_product_active_type
ON product_product(type, is_removed, delete_at)
WHERE is_removed = FALSE AND delete_at IS NULL;

-- Categories & Brands (para LEFT JOIN en products)
CREATE INDEX CONCURRENTLY idx_category_removed
ON category_category(id)
WHERE is_removed = FALSE AND delete_at IS NULL;

CREATE INDEX CONCURRENTLY idx_brand_removed
ON brand_brand(id)
WHERE is_removed = FALSE AND delete_at IS NULL;

-- ============================================================
-- ACTUALIZAR ESTADÍSTICAS (IMPORTANTE)
-- ============================================================

ANALYZE customer_customer;
ANALYZE bank_accounts_bankaccounts;
ANALYZE list_price_pricelist;
ANALYZE list_price_pricelistdetail;
ANALYZE customer_customer_list_price;
ANALYZE location_location;
ANALYZE cobranza_cobranza;
ANALYZE cobranza_cobranzadetail;
ANALYZE product_product;
ANALYZE category_category;
ANALYZE brand_brand;
```

**Impacto estimado:**
- Sin índices con `is_removed`: +30% más lento
- Con índices optimizados: **-50% a -75% en queries afectadas**
- Reducción total proyectada: **De 3953ms → ~2200ms** (44% más rápido)

---

### 5. **Read Replica (Opcional)**

Si el tráfico de lectura es muy alto:

```bash
aws rds create-db-instance-read-replica \
  --db-instance-identifier snapshots-read-replica \
  --source-db-instance-identifier snapshots081020232 \
  --db-instance-class db.t3.medium
```

Luego actualiza la Lambda para usar la replica:
```bash
POSTGRES_HOST=snapshots-read-replica.xxx.us-west-2.rds.amazonaws.com
```

**Costo:** Similar a la instancia principal

---

## 📊 Impacto Esperado por Optimización

| Optimización | Impacto en Latencia | Costo Mensual | Prioridad |
|--------------|---------------------|---------------|-----------|
| **Índices en RDS** | -30% a -50% | $0 | 🔴 CRÍTICO |
| **Lambda en VPC** | -50ms a -100ms | $0 | 🔴 CRÍTICO |
| **RDS Proxy** | -100ms a -300ms | ~$11 | 🟡 ALTO |
| **VPC Endpoints** | Variable | ~$7.50/endpoint | 🟢 MEDIO |
| **Evitar NAT** | -10ms a -30ms | Ahorra $32 | 🟢 MEDIO |
| **Parameter Group** | -10% a -20% | $0 | 🟢 BAJO |

---

## 🎯 Plan de Implementación Recomendado

### Fase 1: Sin Costo (Hacer YA) 🔴 CRÍTICO

**Estado actual:** 3953ms con `is_removed = FALSE` pero SIN índices

1. ✅ **Optimizaciones de código ya aplicadas:**
   - geofence::text (CUSTOMERS, LOCATIONS)
   - LEFT JOIN en PRODUCTS
   - Subconsultas IN en COBRANZAS, CLIENT_LIST_PRICES
   - Filtros `is_removed = FALSE` en 7 tablas

2. 🔴 **CREAR ÍNDICES PARCIALES EN RDS** (líneas 169-242)
   - CRÍTICO: Sin estos índices, las queries con `is_removed` son 30-75% más lentas
   - Ejecutar todos los comandos CREATE INDEX CONCURRENTLY
   - Ejecutar ANALYZE en todas las tablas

**Tiempo estimado:** 30 minutos
**Impacto:** **De 3953ms → ~2200ms** (44% más rápido)

### Fase 2: Bajo Costo ($11/mes)
1. ⚠️ **Configurar RDS Proxy**
2. ⚠️ **Actualizar POSTGRES_HOST**

**Tiempo estimado:** 1 hora
**Impacto adicional:** -200ms por invocación

### Fase 3: Rediseño de Red (Requiere planificación)
1. 🔵 **Migrar Lambda a VPC**
2. 🔵 **Configurar Security Groups**
3. 🔵 **Crear VPC Endpoints** (en lugar de NAT)

**Tiempo estimado:** 2-4 horas
**Impacto adicional:** -50ms a -100ms

---

## 🔍 Verificar Configuración Actual

### 1. ¿Tu Lambda está en VPC?

```bash
aws lambda get-function-configuration --function-name ExportSQLiteFunction \
  --query 'VpcConfig'
```

**Si retorna `null`:** Lambda NO está en VPC (latencia alta)

### 2. ¿Qué índices tienes en RDS?

```sql
-- Conectarse a PostgreSQL y ejecutar:
SELECT
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;
```

### 3. ¿Estás usando NAT Gateway?

```bash
aws ec2 describe-nat-gateways --filter "Name=state,Values=available"
```

---

## ⚡ Resultado Esperado Final

### Progresión de Mejoras

| Etapa | Tiempo | vs Original | Descripción |
|-------|--------|-------------|-------------|
| **Original (sin optimizar)** | 4560 ms | - | Código base sin optimizaciones |
| **Con queries optimizadas** | 3192 ms | -30% | geofence::text, LEFT JOIN, subconsultas |
| **+ is_removed filter (sin índices)** | 3953 ms | -13% | Filtrado correcto pero sin índices ⚠️ |
| **+ Índices parciales** | ~2200 ms | -52% | ✅ HACER ESTO PRIMERO |
| **+ RDS Proxy** | ~1900 ms | -58% | Reutilización de conexiones |
| **+ Lambda en VPC** | ~1600 ms | -65% | Latencia de red reducida |

### 🎯 Objetivo Recomendado

**Con Fase 1 (índices):**
- **De 4560ms → 2200ms = -52% de mejora** ⚡
- Costo: $0
- Tiempo: 30 minutos

**Con Fase 1 + Fase 2 (+ RDS Proxy):**
- **De 4560ms → 1900ms = -58% de mejora** 🚀
- Costo adicional: ~$11/mes
- Tiempo adicional: 1 hora

**Óptimo (Todas las fases):**
- **De 4560ms → 1600ms = -65% de mejora total** 🏆
