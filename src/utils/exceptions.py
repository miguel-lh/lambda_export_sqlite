"""
Excepciones personalizadas para la aplicación.
Sigue el principio DRY (Don't Repeat Yourself).
"""


class ExportError(Exception):
    """Excepción base para errores de exportación."""
    pass


class DatabaseConnectionError(ExportError):
    """Error al conectar a la base de datos."""
    pass


class DataFetchError(ExportError):
    """Error al obtener datos de la base de datos."""
    pass


class SQLiteCreationError(ExportError):
    """Error al crear el archivo SQLite."""
    pass


class ValidationError(ExportError):
    """Error de validación de datos."""
    pass
