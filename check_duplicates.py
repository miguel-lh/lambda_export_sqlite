#!/usr/bin/env python3
"""Script para verificar duplicados en las queries de PostgreSQL."""
import sys
import os
from collections import Counter

sys.path.insert(0, 'src')

os.environ.update({
    'POSTGRES_HOST': 'snapshots081020232.crgij3iw0xe0.us-west-2.rds.amazonaws.com',
    'POSTGRES_PORT': '5432',
    'POSTGRES_DATABASE': 'production',
    'POSTGRES_USER': 'af_master',
    'POSTGRES_PASSWORD': 'af_master9021A',
})

from infrastructure.postgres_repository import PostgresRepository

repo = PostgresRepository(
    host=os.environ['POSTGRES_HOST'],
    port=int(os.environ['POSTGRES_PORT']),
    database=os.environ['POSTGRES_DATABASE'],
    user=os.environ['POSTGRES_USER'],
    password=os.environ['POSTGRES_PASSWORD']
)

TENANT_ID = 64127

print("=" * 70)
print("VERIFICANDO DUPLICADOS EN QUERIES")
print("=" * 70)
print(f"Tenant ID: {TENANT_ID}\n")

repo.connect()

def check_duplicates(name, items, id_getter=lambda x: x.id):
    """Verifica duplicados en una lista de items."""
    ids = [id_getter(item) for item in items]
    id_counts = Counter(ids)
    duplicates = {id: count for id, count in id_counts.items() if count > 1}

    total = len(ids)
    unique = len(set(ids))
    dup_count = total - unique

    status = "✅" if dup_count == 0 else "❌"
    print(f"{status} {name}:")
    print(f"   Total: {total} | Únicos: {unique} | Duplicados: {dup_count}")

    if duplicates:
        print(f"   IDs duplicados:")
        for id, count in list(duplicates.items())[:5]:
            print(f"     - ID {id}: aparece {count} veces")
        if len(duplicates) > 5:
            print(f"     ... y {len(duplicates) - 5} más")
    print()

    return dup_count == 0

# Verificar cada tabla
all_ok = True

print("1. CUSTOMERS")
customers = repo.get_customers_by_tenant(TENANT_ID)
all_ok &= check_duplicates("Customers", customers)

print("2. PRODUCTS")
products = repo.get_products_by_tenant(TENANT_ID)
all_ok &= check_duplicates("Products", products)

print("3. BANK ACCOUNTS")
bank_accounts = repo.get_bank_accounts_by_tenant(TENANT_ID)
all_ok &= check_duplicates("Bank Accounts", bank_accounts)

print("4. LIST PRICES")
list_prices = repo.get_list_prices_by_tenant(TENANT_ID)
all_ok &= check_duplicates("List Prices", list_prices)

print("5. LIST PRICE DETAILS")
list_price_details = repo.get_list_price_details_by_tenant(TENANT_ID)
all_ok &= check_duplicates("List Price Details", list_price_details)

print("6. CLIENT LIST PRICES")
client_list_prices = repo.get_client_list_prices_by_tenant(TENANT_ID)
all_ok &= check_duplicates("Client List Prices", client_list_prices)

print("7. LOCATIONS")
locations = repo.get_locations_by_tenant(TENANT_ID)
all_ok &= check_duplicates("Locations", locations)

print("8. COBRANZAS")
cobranzas = repo.get_cobranzas_by_tenant(TENANT_ID)
all_ok &= check_duplicates("Cobranzas", cobranzas)

print("9. COBRANZA DETAILS")
cobranza_details = repo.get_cobranza_details_by_tenant(TENANT_ID)
all_ok &= check_duplicates("Cobranza Details", cobranza_details)

repo.disconnect()

print("=" * 70)
if all_ok:
    print("✅ NO HAY DUPLICADOS - Todo está bien!")
else:
    print("❌ SE ENCONTRARON DUPLICADOS - Revisa las queries arriba")
print("=" * 70)
