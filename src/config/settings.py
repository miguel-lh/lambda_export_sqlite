"""
Configuración de la aplicación.
Usa Pydantic para validación y gestión de configuración.
Sigue el principio de Responsabilidad Única (SRP).
"""
import os
from typing import Optional

from pydantic_settings import BaseSettings
from pydantic import Field, validator


class Settings(BaseSettings):
    """
    Configuración de la aplicación.
    Lee variables de entorno y las valida.
    """

    # Configuración de PostgreSQL
    postgres_host: str = Field(..., env='POSTGRES_HOST')
    postgres_port: int = Field(default=5432, env='POSTGRES_PORT')
    postgres_database: str = Field(..., env='POSTGRES_DATABASE')
    postgres_user: str = Field(..., env='POSTGRES_USER')
    postgres_password: str = Field(..., env='POSTGRES_PASSWORD')

    # Configuración de la aplicación
    log_level: str = Field(default='INFO', env='LOG_LEVEL')
    environment: str = Field(default='dev', env='ENVIRONMENT')

    # Configuración de archivos temporales
    temp_dir: str = Field(default='/tmp', env='TEMP_DIR')

    @validator('log_level')
    def validate_log_level(cls, v):
        """Valida que el nivel de log sea válido."""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'log_level debe ser uno de {valid_levels}')
        return v.upper()

    @validator('postgres_port')
    def validate_postgres_port(cls, v):
        """Valida que el puerto de PostgreSQL sea válido."""
        if not 1 <= v <= 65535:
            raise ValueError('postgres_port debe estar entre 1 y 65535')
        return v

    class Config:
        """Configuración de Pydantic."""
        env_file = '.env'
        env_file_encoding = 'utf-8'
        case_sensitive = False


def get_settings() -> Settings:
    """
    Obtiene la configuración de la aplicación.
    Implementa patrón Singleton para evitar múltiples lecturas.

    Returns:
        Instancia de Settings
    """
    return Settings()
