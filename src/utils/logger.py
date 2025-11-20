"""
Configuración centralizada de logging.
Sigue el principio DRY (Don't Repeat Yourself).
"""
import logging
import sys
import os
from typing import Optional


def setup_logger(
    name: Optional[str] = None,
    level: Optional[str] = None
) -> logging.Logger:
    """
    Configura y retorna un logger.

    Args:
        name: Nombre del logger (None para root logger)
        level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        Logger configurado
    """
    logger = logging.getLogger(name)

    # Obtener nivel de log de variable de entorno o usar el parámetro
    log_level = level or os.getenv('LOG_LEVEL', 'INFO')
    logger.setLevel(getattr(logging, log_level.upper()))

    # Evitar duplicación de handlers
    if logger.handlers:
        return logger

    # Crear handler para stdout
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, log_level.upper()))

    # Formato para Lambda (JSON-friendly)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Obtiene un logger ya configurado.

    Args:
        name: Nombre del logger

    Returns:
        Logger
    """
    return logging.getLogger(name)
