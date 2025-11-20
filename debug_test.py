#!/usr/bin/env python3
"""Script de debugging detallado."""
import sys
import os
import logging

sys.path.insert(0, 'src')

# Configurar logging detallado
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Variables de entorno
os.environ.update({
    'POSTGRES_HOST': 'snapshots081020232.crgij3iw0xe0.us-west-2.rds.amazonaws.com',
    'POSTGRES_PORT': '5432',
    'POSTGRES_DATABASE': 'production',
    'POSTGRES_USER': 'af_master',
    'POSTGRES_PASSWORD': 'af_master9021A',
    'LOG_LEVEL': 'DEBUG',
    'TEMP_DIR': '/tmp'
})

print("=" * 70)
print("DEBUG TEST - EXPORTACIÓN SQLITE")
print("=" * 70)

print("\n=== PASO 1: Importar módulos ===")
try:
    from infrastructure.postgres_repository import PostgresRepository
    from infrastructure.sqlite_builder import SQLiteBuilder
    from application.export_service import ExportService
    print("✅ Imports exitosos")
except Exception as e:
    print(f"❌ Error en imports: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n=== PASO 2: Crear instancias ===")
try:
    repo = PostgresRepository(
        host=os.environ['POSTGRES_HOST'],
        port=int(os.environ['POSTGRES_PORT']),
        database=os.environ['POSTGRES_DATABASE'],
        user=os.environ['POSTGRES_USER'],
        password=os.environ['POSTGRES_PASSWORD']
    )
    print("  ✅ PostgresRepository creado")

    builder = SQLiteBuilder()
    print("  ✅ SQLiteBuilder creado")

    service = ExportService(repo, builder)
    print("  ✅ ExportService creado")

except Exception as e:
    print(f"❌ Error creando instancias: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n=== PASO 3: Configurar parámetros de exportación ===")
tenant_id = 1  # CAMBIA ESTE VALOR por un tenant_id real
output_path = '/tmp/test_export.sqlite'

print(f"  Tenant ID: {tenant_id}")
print(f"  Output path: {output_path}")

print("\n=== PASO 4: Ejecutar exportación ===")
try:
    result = service.export_tenant_data(tenant_id, output_path)

    print("\n" + "=" * 70)
    print("RESULTADO DE LA EXPORTACIÓN")
    print("=" * 70)

    if result.success:
        print("✅ Exportación exitosa!")
        print(f"\n📁 Archivo:")
        print(f"   Path: {result.file_path}")
        print(f"   Tamaño: {result.file_size:,} bytes ({result.file_size / 1024:.2f} KB)")

        print(f"\n📊 Registros exportados:")
        total_records = 0
        for table, count in result.records_exported.items():
            print(f"   {table:25s}: {count:6d} registros")
            total_records += count
        print(f"   {'TOTAL':25s}: {total_records:6d} registros")

        print(f"\n⏱️  Tiempo de ejecución: {result.execution_time_ms} ms ({result.execution_time_ms / 1000:.2f} segundos)")

        # Verificar el archivo
        if os.path.exists(output_path):
            import sqlite3
            conn = sqlite3.connect(output_path)
            cursor = conn.cursor()

            print(f"\n🔍 Verificación del archivo SQLite:")

            # Obtener lista de tablas
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            print(f"\n   Tablas creadas ({len(tables)}):")
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
                count = cursor.fetchone()[0]
                print(f"     - {table[0]:25s}: {count:6d} registros")

            conn.close()

            print(f"\n💡 Puedes inspeccionar el archivo con:")
            print(f"   sqlite3 {output_path}")
            print(f"   .tables")
            print(f"   SELECT * FROM Customer LIMIT 5;")

    else:
        print("❌ Exportación falló")
        print(f"\n🚫 Error: {result.error_message}")
        if result.records_exported:
            print(f"\n📊 Registros obtenidos antes del error:")
            for table, count in result.records_exported.items():
                print(f"   {table}: {count}")

except Exception as e:
    print("\n" + "=" * 70)
    print("❌ ERROR DURANTE EXPORTACIÓN")
    print("=" * 70)
    print(f"Error: {str(e)}")
    print("\n📋 Stack trace completo:")
    import traceback
    traceback.print_exc()

    print("\n💡 Sugerencias:")
    print("  1. Verifica que el tenant_id existe en la base de datos")
    print("  2. Verifica los nombres de las tablas en postgres_repository.py")
    print("  3. Revisa los logs arriba para ver qué tabla causó el error")
