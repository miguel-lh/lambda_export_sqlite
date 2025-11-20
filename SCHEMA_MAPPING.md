# Mapeo de Esquema PostgreSQL

Este archivo te ayuda a documentar los nombres reales de tus tablas y campos en PostgreSQL.

## Instrucciones

1. Completa los nombres reales de tus tablas
2. Completa los nombres reales de los campos
3. Usa este documento como referencia para editar `src/infrastructure/postgres_repository.py`

---

## 1. Customer (Clientes)

**Nombre de la tabla en PostgreSQL:** `_________________`

| Campo en el código | Campo real en PostgreSQL | Tipo |
|-------------------|-------------------------|------|
| id | | int |
| slug | | text |
| name | | text |
| tel | | text |
| email | | text |
| code | | text |
| sequence | | int |
| format | | text |
| type_sale | | text |
| way_to_pay | | text |
| street | | text |
| ext_number | | text |
| int_number | | text |
| suburb | | text |
| code_postal | | text |
| city | | text |
| state | | text |
| country | | text |
| lat | | text |
| lng | | text |
| geofence | | text |
| sequence_times_from1 | | int |
| sequence_times_up_to1 | | int |
| sequence_times_from2 | | int |
| sequence_times_up_to2 | | int |
| sequence_times_from3 | | int |
| sequence_times_up_to3 | | int |
| is_pay_sun | | boolean |
| is_pay_mon | | boolean |
| is_pay_tues | | boolean |
| is_pay_wed | | boolean |
| is_pay_thurs | | boolean |
| is_pay_fri | | boolean |
| is_pay_sat | | boolean |
| code_netsuit | | text |
| credit_limit | | text |
| checked | | boolean |
| deuda | | text |

**¿Tiene campo tenant_id?** ☐ Sí ☐ No (Si no, ¿cómo filtras por tenant?)

---

## 2. Product (Productos)

**Nombre de la tabla en PostgreSQL:** `_________________`

| Campo en el código | Campo real en PostgreSQL | Tipo |
|-------------------|-------------------------|------|
| id | | int |
| sku | | text |
| name | | text |
| description | | text |
| bard_code | | text |
| type | | text |
| brand | | text |
| category | | text |

**¿Tiene campo tenant_id?** ☐ Sí ☐ No

---

## 3. BankAccount (Cuentas Bancarias)

**Nombre de la tabla en PostgreSQL:** `_________________`

| Campo en el código | Campo real en PostgreSQL | Tipo |
|-------------------|-------------------------|------|
| id | | int |
| name | | text |
| bank_name | | text |
| number | | text |
| accounting_account_name | | text |

**¿Tiene campo tenant_id?** ☐ Sí ☐ No

---

## 4. ListPrice (Listas de Precios)

**Nombre de la tabla en PostgreSQL:** `_________________`

| Campo en el código | Campo real en PostgreSQL | Tipo |
|-------------------|-------------------------|------|
| id | | int |
| name | | text |
| max | | text |
| min | | text |
| customer_sync | | int |

**¿Tiene campo tenant_id?** ☐ Sí ☐ No

---

## 5. ListPriceDetail (Detalle de Lista de Precios)

**Nombre de la tabla en PostgreSQL:** `_________________`

| Campo en el código | Campo real en PostgreSQL | Tipo |
|-------------------|-------------------------|------|
| id | | int |
| id_price_list | | int |
| id_product | | int |
| price | | text |

---

## 6. ClientListPrice (Cliente - Lista de Precios)

**Nombre de la tabla en PostgreSQL:** `_________________`

| Campo en el código | Campo real en PostgreSQL | Tipo |
|-------------------|-------------------------|------|
| id | | int |
| id_client | | int |
| id_list_price | | int |

---

## 7. Location (Ubicaciones)

**Nombre de la tabla en PostgreSQL:** `_________________`

| Campo en el código | Campo real en PostgreSQL | Tipo |
|-------------------|-------------------------|------|
| id | | int |
| slug | | text |
| name | | text |
| tel | | text |
| email | | text |
| code | | text |
| sequence | | int |
| format | | text |
| zone | | text |
| use | | text |
| category | | text |
| type_location | | text |
| street | | text |
| ext_number | | text |
| int_number | | text |
| suburb | | text |
| code_postal | | text |
| city | | text |
| state | | text |
| country | | text |
| lat | | text |
| lng | | text |
| geofence | | text |
| sequence_times_from1 | | int |
| sequence_times_up_to1 | | int |
| sequence_times_from2 | | int |
| sequence_times_up_to2 | | int |
| sequence_times_from3 | | int |
| sequence_times_up_to3 | | int |
| is_pay_sun | | boolean |
| is_pay_mon | | boolean |
| is_pay_tues | | boolean |
| is_pay_wed | | boolean |
| is_pay_thurs | | boolean |
| is_pay_fri | | boolean |
| is_pay_sat | | boolean |
| seller | | text |
| checked | | boolean |

**¿Tiene campo tenant_id?** ☐ Sí ☐ No

---

## 8. Cobranza

**Nombre de la tabla en PostgreSQL:** `_________________`

| Campo en el código | Campo real en PostgreSQL | Tipo |
|-------------------|-------------------------|------|
| id | | int |
| id_client | | int |
| bill_number | | text |
| total | | text |
| issue | | text |
| validity | | text |

---

## 9. CobranzaDetail (Detalle de Cobranza)

**Nombre de la tabla en PostgreSQL:** `_________________`

| Campo en el código | Campo real en PostgreSQL | Tipo |
|-------------------|-------------------------|------|
| id | | int |
| id_cobranza | | int |
| id_product | | int |
| amount | | text |
| price | | text |

---

## Ejemplo de Query Adaptada

### Antes (genérico):
```sql
SELECT
    id,
    name,
    email
FROM customers
WHERE tenant_id = %s
```

### Después (adaptado a tu esquema):
```sql
SELECT
    id,
    nombre AS name,      -- campo se llama 'nombre' en tu DB
    correo AS email      -- campo se llama 'correo' en tu DB
FROM clientes            -- tabla se llama 'clientes'
WHERE tenant_id = %s
```

---

## Pasos para Adaptar

1. ✅ Llena este documento con los nombres reales
2. ✅ Abre `src/infrastructure/postgres_repository.py`
3. ✅ Busca el comentario `-- ADAPTA el nombre de la tabla`
4. ✅ Modifica cada query según tu mapeo
5. ✅ Prueba con un tenant_id real
