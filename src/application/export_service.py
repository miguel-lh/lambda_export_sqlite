"""
Servicio de aplicación para exportar datos a SQLite.
Orquesta las operaciones entre repositorios y builders.
Sigue el principio de Responsabilidad Única (SRP) y el de Inversión de Dependencias (DIP).
"""
import logging
import os
import time
from typing import Dict

from domain.interfaces import IDataRepository, ISQLiteBuilder
from domain.models import ExportResult
from utils.exceptions import ExportError, DatabaseConnectionError

logger = logging.getLogger(__name__)


class ExportService:
    """
    Servicio de exportación de datos.
    Coordina el proceso de exportar datos de PostgreSQL a SQLite.
    """

    def __init__(
        self,
        data_repository: IDataRepository,
        sqlite_builder: ISQLiteBuilder
    ):
        """
        Inicializa el servicio de exportación.

        Args:
            data_repository: Repositorio de datos (PostgreSQL)
            sqlite_builder: Constructor de SQLite
        """
        self.data_repository = data_repository
        self.sqlite_builder = sqlite_builder

    def export_tenant_data(self, tenant_id: int, output_path: str) -> ExportResult:
        """
        Exporta todos los datos de un tenant a un archivo SQLite.

        Args:
            tenant_id: ID del tenant a exportar
            output_path: Ruta del archivo SQLite de salida

        Returns:
            Resultado de la operación de exportación

        Raises:
            DatabaseConnectionError: Si hay error de conexión
            ExportError: Si hay error durante la exportación
        """
        start_time = time.time()
        records_exported: Dict[str, int] = {}

        try:
            # Paso 1: Conectar a PostgreSQL
            logger.info(f"Conectando a PostgreSQL para tenant {tenant_id}")
            self._connect_to_postgres()

            # Paso 2: Obtener datos de PostgreSQL
            logger.info("Obteniendo datos de PostgreSQL")
            customers = self._fetch_data(
                "customers",
                lambda: self.data_repository.get_customers_by_tenant(tenant_id)
            )
            products = self._fetch_data(
                "products",
                lambda: self.data_repository.get_products_by_tenant(tenant_id)
            )
            bank_accounts = self._fetch_data(
                "bank_accounts",
                lambda: self.data_repository.get_bank_accounts_by_tenant(tenant_id)
            )
            list_prices = self._fetch_data(
                "list_prices",
                lambda: self.data_repository.get_list_prices_by_tenant(tenant_id)
            )
            list_price_details = self._fetch_data(
                "list_price_details",
                lambda: self.data_repository.get_list_price_details_by_tenant(tenant_id)
            )
            client_list_prices = self._fetch_data(
                "client_list_prices",
                lambda: self.data_repository.get_client_list_prices_by_tenant(tenant_id)
            )
            locations = self._fetch_data(
                "locations",
                lambda: self.data_repository.get_locations_by_tenant(tenant_id)
            )
            cobranzas = self._fetch_data(
                "cobranzas",
                lambda: self.data_repository.get_cobranzas_by_tenant(tenant_id)
            )
            cobranza_details = self._fetch_data(
                "cobranza_details",
                lambda: self.data_repository.get_cobranza_details_by_tenant(tenant_id)
            )

            # Registrar conteos
            records_exported = {
                'customers': len(customers),
                'products': len(products),
                'bank_accounts': len(bank_accounts),
                'list_prices': len(list_prices),
                'list_price_details': len(list_price_details),
                'client_list_prices': len(client_list_prices),
                'locations': len(locations),
                'cobranzas': len(cobranzas),
                'cobranza_details': len(cobranza_details)
            }

            # Validar que hay datos para exportar
            total_records = sum(records_exported.values())
            if total_records == 0:
                logger.warning(f"No se encontraron datos para tenant {tenant_id}")
                return ExportResult(
                    success=False,
                    error_message=f"No se encontraron datos para el tenant {tenant_id}",
                    records_exported=records_exported,
                    execution_time_ms=int((time.time() - start_time) * 1000)
                )

            # Paso 3: Crear base de datos SQLite
            logger.info(f"Creando base de datos SQLite en {output_path}")
            self._create_sqlite_database(output_path)

            # Paso 4: Insertar datos en SQLite (en orden correcto por relaciones)
            logger.info("Insertando datos en SQLite")
            self._insert_all_data(
                customers=customers,
                products=products,
                bank_accounts=bank_accounts,
                list_prices=list_prices,
                list_price_details=list_price_details,
                client_list_prices=client_list_prices,
                locations=locations,
                cobranzas=cobranzas,
                cobranza_details=cobranza_details
            )

            # Paso 5: Obtener tamaño del archivo
            file_size = os.path.getsize(output_path) if os.path.exists(output_path) else None

            execution_time_ms = int((time.time() - start_time) * 1000)

            logger.info(
                f"Exportación completada exitosamente. "
                f"Registros: {records_exported}, "
                f"Tamaño: {file_size} bytes, "
                f"Tiempo: {execution_time_ms}ms"
            )

            return ExportResult(
                success=True,
                file_path=output_path,
                file_size=file_size,
                records_exported=records_exported,
                execution_time_ms=execution_time_ms
            )

        except Exception as e:
            logger.error(f"Error durante la exportación: {str(e)}", exc_info=True)
            return ExportResult(
                success=False,
                error_message=str(e),
                records_exported=records_exported,
                execution_time_ms=int((time.time() - start_time) * 1000)
            )

        finally:
            # Limpieza de recursos
            self._cleanup()

    def _connect_to_postgres(self) -> None:
        """
        Conecta al repositorio de datos.

        Raises:
            DatabaseConnectionError: Si falla la conexión
        """
        try:
            self.data_repository.connect()
        except Exception as e:
            logger.error(f"Error conectando a PostgreSQL: {e}")
            raise DatabaseConnectionError(f"No se pudo conectar a PostgreSQL: {str(e)}")

    def _fetch_data(self, entity_name: str, fetch_fn):
        """
        Obtiene datos del repositorio con manejo de errores.

        Args:
            entity_name: Nombre de la entidad (para logging)
            fetch_fn: Función que obtiene los datos

        Returns:
            Lista de datos

        Raises:
            ExportError: Si hay error obteniendo los datos
        """
        try:
            return fetch_fn()
        except Exception as e:
            logger.error(f"Error obteniendo {entity_name}: {e}")
            raise ExportError(f"Error obteniendo {entity_name}: {str(e)}")

    def _create_sqlite_database(self, output_path: str) -> None:
        """
        Crea la base de datos SQLite.

        Args:
            output_path: Ruta del archivo

        Raises:
            ExportError: Si hay error creando la base de datos
        """
        try:
            self.sqlite_builder.create_database(output_path)
            self.sqlite_builder.create_schema()
        except Exception as e:
            logger.error(f"Error creando base de datos SQLite: {e}")
            raise ExportError(f"Error creando base de datos SQLite: {str(e)}")

    def _insert_all_data(
        self,
        customers,
        products,
        bank_accounts,
        list_prices,
        list_price_details,
        client_list_prices,
        locations,
        cobranzas,
        cobranza_details
    ) -> None:
        """
        Inserta todos los datos en SQLite.

        IMPORTANTE: El orden de inserción respeta las relaciones de foreign keys.

        Raises:
            ExportError: Si hay error insertando los datos
        """
        try:
            # 1. Insertar tablas base (sin dependencias)
            self.sqlite_builder.insert_customers(customers)
            self.sqlite_builder.insert_products(products)
            self.sqlite_builder.insert_bank_accounts(bank_accounts)
            self.sqlite_builder.insert_list_prices(list_prices)
            self.sqlite_builder.insert_locations(locations)

            # 2. Insertar tablas con foreign keys a las bases
            self.sqlite_builder.insert_list_price_details(list_price_details)
            self.sqlite_builder.insert_client_list_prices(client_list_prices)
            self.sqlite_builder.insert_cobranzas(cobranzas)

            # 3. Insertar tablas con foreign keys a las secundarias
            self.sqlite_builder.insert_cobranza_details(cobranza_details)

        except Exception as e:
            logger.error(f"Error insertando datos en SQLite: {e}")
            raise ExportError(f"Error insertando datos en SQLite: {str(e)}")

    def _cleanup(self) -> None:
        """Limpia recursos y cierra conexiones."""
        try:
            if self.data_repository:
                self.data_repository.disconnect()
        except Exception as e:
            logger.warning(f"Error cerrando repositorio de datos: {e}")

        try:
            if self.sqlite_builder:
                self.sqlite_builder.close()
        except Exception as e:
            logger.warning(f"Error cerrando SQLite builder: {e}")
