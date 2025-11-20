# Ejemplos de Adaptación de Queries

Este documento muestra ejemplos concretos de cómo adaptar las queries en `postgres_repository.py`

## Ejemplo 1: Tabla con nombres diferentes

### Escenario
- Tu tabla se llama `clientes` (no `customers`)
- El campo `name` se llama `nombre`
- El campo `email` se llama `correo_electronico`
- El campo `tel` se llama `telefono`

### Query ANTES (genérica):
```python
def get_customers_by_tenant(self, tenant_id: int) -> List[Customer]:
    query = """
        SELECT
            id,
            slug,
            name,
            tel,
            email,
            code
        FROM customers
        WHERE tenant_id = %s
    """
```

### Query DESPUÉS (adaptada):
```python
def get_customers_by_tenant(self, tenant_id: int) -> List[Customer]:
    query = """
        SELECT
            id,
            slug,
            nombre AS name,                    -- ← Usar AS para mapear
            telefono AS tel,                   -- ← Mapeo de nombre
            correo_electronico AS email,       -- ← Mapeo de nombre
            codigo AS code                     -- ← Mapeo de nombre
        FROM clientes                          -- ← Nombre real de tabla
        WHERE tenant_id = %s
    """
```

## Ejemplo 2: Campos que no existen

### Escenario
- Tu tabla `customers` NO tiene el campo `geofence`
- Tu tabla NO tiene los campos `sequence_times_from1`, etc.

### Query DESPUÉS (campos omitidos):
```python
def get_customers_by_tenant(self, tenant_id: int) -> List[Customer]:
    query = """
        SELECT
            id,
            slug,
            name,
            tel,
            email,
            code,
            NULL AS geofence,                  -- ← Campo que no existe
            NULL AS sequence_times_from1,      -- ← Campo que no existe
            NULL AS sequence_times_up_to1,     -- ← Campo que no existe
            street,
            city
        FROM customers
        WHERE tenant_id = %s
    """

    # El mapeo al modelo funciona igual, solo que esos campos serán None
    customers = [
        Customer(
            id=row['id'],
            slug=row.get('slug'),
            name=row.get('name'),
            geofence=row.get('geofence'),      # ← Será None
            # ... resto de campos
        )
        for row in rows
    ]
```

## Ejemplo 3: Tabla sin tenant_id

### Escenario
- Tu tabla `products` NO tiene campo `tenant_id`
- Los productos están relacionados a tenant por otra tabla

### Opción A: JOIN con tabla que tiene tenant_id
```python
def get_products_by_tenant(self, tenant_id: int) -> List[Product]:
    query = """
        SELECT DISTINCT
            p.id,
            p.sku,
            p.name,
            p.description,
            p.category
        FROM products p
        INNER JOIN product_tenant pt ON p.id = pt.product_id
        WHERE pt.tenant_id = %s
        ORDER BY p.id
    """
```

### Opción B: Traer todos los productos (sin filtro)
```python
def get_products_by_tenant(self, tenant_id: int) -> List[Product]:
    # Si todos los tenants comparten los mismos productos
    query = """
        SELECT
            id,
            sku,
            name,
            description,
            category
        FROM products
        ORDER BY id
    """
    # Nota: No se usa tenant_id en este caso
```

## Ejemplo 4: Campos con tipos diferentes

### Escenario
- `price` es DECIMAL en PostgreSQL pero lo almacenas como TEXT en SQLite

### Query correcta:
```python
query = """
    SELECT
        id,
        product_id,
        price::TEXT AS price,              -- ← Convertir a TEXT
        CAST(amount AS TEXT) AS amount     -- ← Alternativa con CAST
    FROM list_price_details
    WHERE id_price_list = %s
"""
```

## Ejemplo 5: Campos calculados

### Escenario
- Quieres calcular `deuda` sumando facturas pendientes

### Query con campo calculado:
```python
query = """
    SELECT
        c.id,
        c.name,
        c.email,
        COALESCE(
            (SELECT SUM(total)
             FROM invoices i
             WHERE i.customer_id = c.id
             AND i.status = 'pending'),
            0
        )::TEXT AS deuda                   -- ← Campo calculado
    FROM customers c
    WHERE c.tenant_id = %s
"""
```

## Ejemplo 6: Relaciones complejas

### Escenario (ClientListPrice)
- La tabla relaciona clientes con listas de precios
- Necesitas filtrar por tenant del cliente

### Query correcta:
```python
def get_client_list_prices_by_tenant(self, tenant_id: int) -> List[ClientListPrice]:
    query = """
        SELECT
            clp.id,
            clp.customer_id AS id_client,      -- ← Mapeo de nombre
            clp.price_list_id AS id_list_price -- ← Mapeo de nombre
        FROM customer_price_lists clp          -- ← Nombre real
        INNER JOIN customers c ON clp.customer_id = c.id
        WHERE c.tenant_id = %s
        ORDER BY clp.id
    """
```

## Checklist de Adaptación

Para cada método en `postgres_repository.py`:

1. ☐ Identificar el nombre real de la tabla en PostgreSQL
2. ☐ Mapear cada campo del SELECT con AS si el nombre es diferente
3. ☐ Usar NULL AS campo para campos que no existen
4. ☐ Verificar que el WHERE filtra correctamente por tenant_id
5. ☐ Si no hay tenant_id, usar JOIN o estrategia alternativa
6. ☐ Convertir tipos si es necesario (::TEXT, CAST, etc.)
7. ☐ Probar la query en PostgreSQL antes de integrarla

## Herramienta de Ayuda

Puedes probar tus queries directamente en PostgreSQL:

```sql
-- Reemplaza 123 con un tenant_id real
SELECT
    id,
    nombre AS name,
    correo AS email
FROM clientes
WHERE tenant_id = 123
LIMIT 5;
```

## Archivos a Modificar

**SOLO necesitas modificar:**
- `src/infrastructure/postgres_repository.py` (las 9 queries)

**NO necesitas modificar:**
- `src/domain/models.py` ✅ Ya está correcto
- `src/infrastructure/sqlite_builder.py` ✅ Ya está correcto
- `src/application/export_service.py` ✅ Ya está correcto
- Ningún otro archivo

## Ubicación Exacta en el Código

Busca estas líneas en `postgres_repository.py`:

```python
# Línea ~72
def get_customers_by_tenant(self, tenant_id: int) -> List[Customer]:
    query = """
        SELECT ...
        FROM customers  -- ← AQUÍ cambias el nombre

# Línea ~179
def get_products_by_tenant(self, tenant_id: int) -> List[Product]:
    query = """
        SELECT ...
        FROM products  -- ← AQUÍ cambias el nombre

# ... y así para los otros 7 métodos
```
