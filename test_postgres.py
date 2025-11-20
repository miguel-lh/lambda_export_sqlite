#!/usr/bin/env python3
"""Test de conexión y queries a PostgreSQL."""
import sys
import os
sys.path.insert(0, 'src')

# Configurar variables de entorno
os.environ['POSTGRES_HOST'] = 'snapshots081020232.crgij3iw0xe0.us-west-2.rds.amazonaws.com'
os.environ['POSTGRES_PORT'] = '5432'
os.environ['POSTGRES_DATABASE'] = 'production'
os.environ['POSTGRES_USER'] = 'af_master'
os.environ['POSTGRES_PASSWORD'] = 'af_master9021A'

from infrastructure.postgres_repository import PostgresRepository

# Crear repositorio
repo = PostgresRepository(
    host=os.environ['POSTGRES_HOST'],
    port=int(os.environ['POSTGRES_PORT']),
    database=os.environ['POSTGRES_DATABASE'],
    user=os.environ['POSTGRES_USER'],
    password=os.environ['POSTGRES_PASSWORD']
)

# Tenant ID a probar (CÁMBIALO por uno real de tu DB)
TENANT_ID = 64127

print("=" * 60)
print("TEST DE CONEXIÓN A POSTGRESQL")
print("=" * 60)
print(f"Host: {os.environ['POSTGRES_HOST']}")
print(f"Database: {os.environ['POSTGRES_DATABASE']}")
print(f"Tenant ID: {TENANT_ID}")
print("=" * 60)

try:
    print("\n1. Conectando a PostgreSQL...")
    repo.connect()
    print("   ✅ Conexión exitosa!")

    print("\n2. Probando query de customers...")
    try:
        customers = repo.get_customers_by_tenant(TENANT_ID)
        print(f"   ✅ Obtenidos {len(customers)} customers")
        if customers:
            print(f"   Primer customer ID: {customers[0].id}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    print("\n3. Probando query de products...")
    try:
        products = repo.get_products_by_tenant(TENANT_ID)
        print(f"   ✅ Obtenidos {len(products)} products")
        if products:
            print(f"   Primer product ID: {products[0].id}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    print("\n4. Probando query de bank_accounts...")
    try:
        bank_accounts = repo.get_bank_accounts_by_tenant(TENANT_ID)
        print(f"   ✅ Obtenidos {len(bank_accounts)} bank accounts")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    print("\n5. Probando query de list_prices...")
    try:
        list_prices = repo.get_list_prices_by_tenant(TENANT_ID)
        print(f"   ✅ Obtenidos {len(list_prices)} list prices")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    print("\n6. Probando query de list_price_details...")
    try:
        list_price_details = repo.get_list_price_details_by_tenant(TENANT_ID)
        print(f"   ✅ Obtenidos {len(list_price_details)} list price details")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    print("\n7. Probando query de client_list_prices...")
    try:
        client_list_prices = repo.get_client_list_prices_by_tenant(TENANT_ID)
        print(f"   ✅ Obtenidos {len(client_list_prices)} client list prices")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    print("\n8. Probando query de locations...")
    try:
        locations = repo.get_locations_by_tenant(TENANT_ID)
        print(f"   ✅ Obtenidos {len(locations)} locations")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    print("\n9. Probando query de cobranzas...")
    try:
        cobranzas = repo.get_cobranzas_by_tenant(TENANT_ID)
        print(f"   ✅ Obtenidos {len(cobranzas)} cobranzas")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    print("\n10. Probando query de cobranza_details...")
    try:
        cobranza_details = repo.get_cobranza_details_by_tenant(TENANT_ID)
        print(f"   ✅ Obtenidos {len(cobranza_details)} cobranza details")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    repo.disconnect()
    print("\n" + "=" * 60)
    print("✅ TEST COMPLETADO")
    print("=" * 60)

except Exception as e:
    print(f"\n❌ Error de conexión: {e}")
    import traceback
    traceback.print_exc()
