#!/usr/bin/env python3
"""Script de prueba local para la Lambda."""
import sys
import os

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Configurar variables de entorno
os.environ['POSTGRES_HOST'] = 'snapshots081020232.crgij3iw0xe0.us-west-2.rds.amazonaws.com'
os.environ['POSTGRES_PORT'] = '5432'
os.environ['POSTGRES_DATABASE'] = 'production'
os.environ['POSTGRES_USER'] = 'af_master'
os.environ['POSTGRES_PASSWORD'] = 'af_master9021A'
os.environ['LOG_LEVEL'] = 'DEBUG'
os.environ['ENVIRONMENT'] = 'dev'
os.environ['TEMP_DIR'] = '/tmp'

# Importar el handler
from handler import lambda_handler

# Evento de prueba
event = {
    'pathParameters': {
        'tenant_id': '1843'  # <- Cambia por un tenant_id real de tu DB
    }
}

# Contexto mock
class MockContext:
    def __init__(self):
        self.function_name = 'test'
        self.memory_limit_in_mb = 128
        self.invoked_function_arn = 'arn:aws:lambda:us-east-1:123456789012:function:test'
        self.aws_request_id = 'test-request-id'

# Ejecutar
if __name__ == '__main__':
    print("=" * 60)
    print("Ejecutando Lambda localmente...")
    print("=" * 60)
    print(f"Tenant ID: {event['pathParameters']['tenant_id']}")
    print(f"Database: {os.environ['POSTGRES_DATABASE']}")
    print(f"Host: {os.environ['POSTGRES_HOST']}")
    print("=" * 60)

    try:
        result = lambda_handler(event, MockContext())

        print("\n" + "=" * 60)
        print("RESULTADO")
        print("=" * 60)
        print(f"Status Code: {result['statusCode']}")

        if result['statusCode'] == 200:
            print("✅ Exportación exitosa!")

            # Obtener los headers con información de tiempos
            headers = result.get('headers', {})
            execution_time = headers.get('X-Execution-Time-Ms', 'N/A')
            file_size = headers.get('X-File-Size', 'N/A')

            print(f"\n" + "=" * 60)
            print("📊 TIEMPOS DE EJECUCIÓN")
            print("=" * 60)
            print(f"⏱️  Tiempo total de ejecución: {execution_time} ms")

            # Si el resultado tiene metadata, mostrar tiempos detallados
            if 'metadata' in result:
                metadata = result['metadata']
                postgres_time = metadata.get('postgres_fetch_time_ms', 'N/A')
                sqlite_time = metadata.get('sqlite_build_time_ms', 'N/A')
                fetch_times = metadata.get('fetch_times_by_table', {})

                print(f"🔍 Tiempo extracción PostgreSQL: {postgres_time} ms")
                print(f"🏗️  Tiempo construcción SQLite: {sqlite_time} ms")

                # Calcular porcentajes si tenemos los datos
                if postgres_time != 'N/A' and sqlite_time != 'N/A' and execution_time != 'N/A':
                    total = int(execution_time)
                    postgres_pct = (int(postgres_time) / total * 100) if total > 0 else 0
                    sqlite_pct = (int(sqlite_time) / total * 100) if total > 0 else 0
                    print(f"\n📈 Distribución del tiempo:")
                    print(f"   - PostgreSQL: {postgres_pct:.1f}%")
                    print(f"   - SQLite: {sqlite_pct:.1f}%")
                    print(f"   - Otros: {100 - postgres_pct - sqlite_pct:.1f}%")

                # Mostrar tiempos por tabla si están disponibles
                if fetch_times:
                    print(f"\n" + "=" * 60)
                    print("⏲️  TIEMPOS DE EXTRACCIÓN POR TABLA")
                    print("=" * 60)
                    # Ordenar por tiempo (de mayor a menor)
                    sorted_times = sorted(fetch_times.items(), key=lambda x: x[1], reverse=True)
                    for table_name, table_time in sorted_times:
                        # Obtener número de registros para esta tabla
                        records_count = metadata.get('records_exported', {}).get(table_name, 0)
                        records_per_sec = (records_count / (table_time / 1000)) if table_time > 0 else 0
                        print(f"  {table_name:20s}: {table_time:5d} ms  ({records_count:6d} registros, {records_per_sec:7.0f} reg/s)")

                    # Calcular estadísticas
                    total_fetch_time = sum(fetch_times.values())
                    print(f"\n  Suma de tiempos individuales: {total_fetch_time} ms")
                    print(f"  Tiempo real (paralelo): {postgres_time} ms")
                    if postgres_time != 'N/A' and total_fetch_time > 0:
                        speedup = total_fetch_time / int(postgres_time)
                        print(f"  Factor de aceleración: {speedup:.2f}x")

                # Mostrar tiempos detallados de queries si están disponibles
                query_timings = metadata.get('query_timings_detailed', {})
                if query_timings:
                    print(f"\n" + "=" * 60)
                    print("🔍 TIEMPOS DETALLADOS DE QUERIES")
                    print("=" * 60)
                    for table_name, timings in query_timings.items():
                        print(f"\n📊 {table_name.upper()}:")
                        print(f"  ├─ Tiempo SQL (execute):   {timings.get('execute_time_ms', 0):8.2f} ms")
                        print(f"  ├─ Tiempo Fetch:           {timings.get('fetch_time_ms', 0):8.2f} ms")
                        print(f"  ├─ Tiempo Procesamiento:   {timings.get('process_time_ms', 0):8.2f} ms")
                        print(f"  ├─ Tiempo Total DB:        {timings.get('db_time_ms', 0):8.2f} ms")
                        print(f"  └─ Tiempo Total Función:   {timings.get('total_time_ms', 0):8.2f} ms")

                        # Calcular porcentajes
                        total_func = timings.get('total_time_ms', 0)
                        if total_func > 0:
                            exec_pct = (timings.get('execute_time_ms', 0) / total_func) * 100
                            fetch_pct = (timings.get('fetch_time_ms', 0) / total_func) * 100
                            process_pct = (timings.get('process_time_ms', 0) / total_func) * 100
                            print(f"     Distribución: Execute {exec_pct:.1f}%, Fetch {fetch_pct:.1f}%, Process {process_pct:.1f}%")

                print(f"\n" + "=" * 60)
                print("📦 INFORMACIÓN DEL ARCHIVO")
                print("=" * 60)
                print(f"  - Tamaño archivo: {file_size} bytes ({int(file_size)/1024:.2f} KB)" if file_size != 'N/A' else f"  - Tamaño archivo: {file_size}")
                print(f"\n" + "=" * 60)
                print("📋 REGISTROS EXPORTADOS")
                print("=" * 60)
                total_records = 0
                for table, count in metadata.get('records_exported', {}).items():
                    print(f"  - {table}: {count}")
                    total_records += count
                print(f"\n  🔢 Total de registros: {total_records}")

            # Mostrar información del archivo
            if result.get('isBase64Encoded'):
                import base64
                file_data = base64.b64decode(result['body'])
                print(f"\n📦 Archivo SQLite generado: {len(file_data)} bytes")

                # Guardar el archivo en la carpeta Descargas
                tenant_id = event['pathParameters']['tenant_id']
                downloads_dir = os.path.expanduser('~/Downloads')
                output_file = os.path.join(downloads_dir, f'database_catalog_master_{tenant_id}.sqlite')
                with open(output_file, 'wb') as f:
                    f.write(file_data)
                print(f"💾 Archivo guardado en: {output_file}")
                print(f"\nPuedes inspeccionarlo con: sqlite3 {output_file}")
        else:
            print("❌ Error en la exportación")
            import json
            body = json.loads(result.get('body', '{}'))
            print(f"\nError: {body.get('error', 'Unknown error')}")

    except Exception as e:
        print("\n" + "=" * 60)
        print("❌ ERROR DURANTE LA EJECUCIÓN")
        print("=" * 60)
        print(f"Error: {str(e)}")
        print("\nStack trace:")
        import traceback
        traceback.print_exc()
