"""
Lambda handler - Punto de entrada de la función Lambda.
Orquesta la creación de dependencias y ejecuta el servicio de exportación.
"""
import json
import os
import base64
from typing import Dict, Any

from config.settings import get_settings
from utils.logger import setup_logger
from infrastructure.postgres_repository import PostgresRepository
from infrastructure.sqlite_builder import SQLiteBuilder
from application.export_service import ExportService

# Configurar logger
logger = setup_logger(__name__)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handler principal de la función Lambda.

    Args:
        event: Evento de API Gateway con pathParameters conteniendo tenant_id
        context: Contexto de Lambda

    Returns:
        Respuesta HTTP con el archivo SQLite en base64 o error
    """
    logger.info(f"Recibido evento: {json.dumps(event)}")

    try:
        # Obtener tenant_id del path
        tenant_id = _extract_tenant_id(event)
        logger.info(f"Procesando exportación para tenant: {tenant_id}")

        # Cargar configuración
        settings = get_settings()

        # Crear ruta temporal para el archivo SQLite
        output_path = os.path.join(settings.temp_dir, f"database_catalog_master_{tenant_id}.sqlite")

        # Crear dependencias (Inyección de Dependencias)
        postgres_repo = _create_postgres_repository(settings)
        sqlite_builder = SQLiteBuilder()

        # Crear servicio de exportación
        export_service = ExportService(
            data_repository=postgres_repo,
            sqlite_builder=sqlite_builder
        )

        # Ejecutar exportación
        result = export_service.export_tenant_data(tenant_id, output_path)

        # Verificar resultado
        if not result.success:
            logger.error(f"Exportación falló: {result.error_message}")
            return _error_response(
                status_code=500,
                message=result.error_message or "Error durante la exportación"
            )

        # Leer archivo SQLite y convertir a base64
        with open(output_path, 'rb') as f:
            sqlite_data = f.read()

        # Guardar el tamaño del archivo binario original
        binary_size = len(sqlite_data)

        sqlite_base64 = base64.b64encode(sqlite_data).decode('utf-8')

        # Limpiar archivo temporal
        if os.path.exists(output_path):
            os.remove(output_path)
            logger.info(f"Archivo temporal eliminado: {output_path}")

        # Retornar respuesta con archivo binario
        # API Gateway decodificará automáticamente el base64 a binario
        # cuando el Content-Type esté en BinaryMediaTypes
        logger.info(f"Exportación exitosa: {result.to_dict()}")
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/x-sqlite3',  # Tipo MIME específico para SQLite
                'Content-Disposition': f'attachment; filename="database_catalog_master_{tenant_id}.sqlite"',
                'Content-Length': str(binary_size),
                'Cache-Control': 'no-cache, no-store, no-transform',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Expose-Headers': 'Content-Length, Content-Type, X-File-Size',
                'X-Tenant-Id': str(tenant_id),
                'X-File-Size': str(result.file_size),
                'X-Execution-Time-Ms': str(result.execution_time_ms),
                'X-Postgres-Fetch-Time-Ms': str(result.postgres_fetch_time_ms),
                'X-Sqlite-Build-Time-Ms': str(result.sqlite_build_time_ms)
            },
            'body': sqlite_base64,
            'isBase64Encoded': True  # API Gateway decodificará esto a binario puro
        }

    except ValueError as e:
        logger.error(f"Error de validación: {str(e)}")
        return _error_response(status_code=400, message=str(e))

    except Exception as e:
        logger.error(f"Error inesperado: {str(e)}", exc_info=True)
        return _error_response(
            status_code=500,
            message="Error interno del servidor"
        )


def _extract_tenant_id(event: Dict[str, Any]) -> int:
    """
    Extrae y valida el tenant_id del evento.

    Args:
        event: Evento de Lambda

    Returns:
        tenant_id como entero

    Raises:
        ValueError: Si el tenant_id no es válido
    """
    # Intentar obtener de pathParameters
    path_params = event.get('pathParameters', {})
    if path_params and 'tenant_id' in path_params:
        tenant_id_str = path_params['tenant_id']
    # Intentar obtener de queryStringParameters
    elif event.get('queryStringParameters', {}) and 'tenant_id' in event.get('queryStringParameters', {}):
        tenant_id_str = event['queryStringParameters']['tenant_id']
    else:
        raise ValueError("tenant_id es requerido en pathParameters o queryStringParameters")

    try:
        tenant_id = int(tenant_id_str)
        if tenant_id <= 0:
            raise ValueError("tenant_id debe ser un número positivo")
        return tenant_id
    except (ValueError, TypeError):
        raise ValueError(f"tenant_id inválido: {tenant_id_str}")


def _create_postgres_repository(settings) -> PostgresRepository:
    """
    Crea una instancia del repositorio de PostgreSQL.

    Args:
        settings: Configuración de la aplicación

    Returns:
        Instancia de PostgresRepository
    """
    return PostgresRepository(
        host=settings.postgres_host,
        port=settings.postgres_port,
        database=settings.postgres_database,
        user=settings.postgres_user,
        password=settings.postgres_password
    )


def _error_response(status_code: int, message: str) -> Dict[str, Any]:
    """
    Crea una respuesta de error HTTP.

    Args:
        status_code: Código de estado HTTP
        message: Mensaje de error

    Returns:
        Respuesta HTTP formateada
    """
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'error': message,
            'status': status_code
        })
    }
