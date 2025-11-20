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
        'tenant_id': '64127'  # <- Cambia por un tenant_id real de tu DB
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
            if 'metadata' in result:
                print(f"\nMetadata:")
                metadata = result['metadata']
                print(f"  - Tenant ID: {metadata.get('tenant_id')}")
                print(f"  - Tamaño archivo: {metadata.get('file_size')} bytes")
                print(f"  - Tiempo ejecución: {metadata.get('execution_time_ms')} ms")
                print(f"\nRegistros exportados:")
                for table, count in metadata.get('records_exported', {}).items():
                    print(f"  - {table}: {count}")

            # Mostrar información del archivo
            if result.get('isBase64Encoded'):
                import base64
                file_data = base64.b64decode(result['body'])
                print(f"\n📦 Archivo SQLite generado: {len(file_data)} bytes")

                # Guardar el archivo localmente para inspección
                output_file = '/tmp/exported.sqlite'
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
