"""
Interfaces (contratos) para la aplicación.
Siguiendo el principio de Inversión de Dependencias (DIP) de SOLID.
Las capas de alto nivel dependen de abstracciones, no de implementaciones concretas.
"""
from abc import ABC, abstractmethod
from typing import List

from src.domain.models import (
    Customer, Product, BankAccount, ListPrice, ListPriceDetail,
    ClientListPrice, Location, Cobranza, CobranzaDetail
)


class IDataRepository(ABC):
    """
    Interfaz para repositorios de datos.
    Define el contrato para acceder a datos sin especificar la fuente.
    """

    @abstractmethod
    def connect(self) -> None:
        """Establece conexión con la fuente de datos."""
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Cierra la conexión con la fuente de datos."""
        pass

    @abstractmethod
    def get_customers_by_tenant(self, tenant_id: int) -> List[Customer]:
        """Obtiene todos los clientes de un tenant."""
        pass

    @abstractmethod
    def get_products_by_tenant(self, tenant_id: int) -> List[Product]:
        """Obtiene todos los productos de un tenant."""
        pass

    @abstractmethod
    def get_bank_accounts_by_tenant(self, tenant_id: int) -> List[BankAccount]:
        """Obtiene todas las cuentas bancarias de un tenant."""
        pass

    @abstractmethod
    def get_list_prices_by_tenant(self, tenant_id: int) -> List[ListPrice]:
        """Obtiene todas las listas de precios de un tenant."""
        pass

    @abstractmethod
    def get_list_price_details_by_tenant(self, tenant_id: int) -> List[ListPriceDetail]:
        """Obtiene todos los detalles de listas de precios de un tenant."""
        pass

    @abstractmethod
    def get_client_list_prices_by_tenant(self, tenant_id: int) -> List[ClientListPrice]:
        """Obtiene todas las relaciones cliente-lista de precios de un tenant."""
        pass

    @abstractmethod
    def get_locations_by_tenant(self, tenant_id: int) -> List[Location]:
        """Obtiene todas las ubicaciones de un tenant."""
        pass

    @abstractmethod
    def get_cobranzas_by_tenant(self, tenant_id: int) -> List[Cobranza]:
        """Obtiene todas las cobranzas de un tenant."""
        pass

    @abstractmethod
    def get_cobranza_details_by_tenant(self, tenant_id: int) -> List[CobranzaDetail]:
        """Obtiene todos los detalles de cobranza de un tenant."""
        pass


class ISQLiteBuilder(ABC):
    """
    Interfaz para construcción de archivos SQLite.
    Define el contrato para crear y poblar bases de datos SQLite.
    """

    @abstractmethod
    def create_database(self, file_path: str) -> None:
        """Crea una nueva base de datos SQLite."""
        pass

    @abstractmethod
    def create_schema(self) -> None:
        """Crea el esquema de tablas en la base de datos."""
        pass

    @abstractmethod
    def insert_customers(self, customers: List[Customer]) -> int:
        """Inserta clientes en la base de datos."""
        pass

    @abstractmethod
    def insert_products(self, products: List[Product]) -> int:
        """Inserta productos en la base de datos."""
        pass

    @abstractmethod
    def insert_bank_accounts(self, bank_accounts: List[BankAccount]) -> int:
        """Inserta cuentas bancarias en la base de datos."""
        pass

    @abstractmethod
    def insert_list_prices(self, list_prices: List[ListPrice]) -> int:
        """Inserta listas de precios en la base de datos."""
        pass

    @abstractmethod
    def insert_list_price_details(self, list_price_details: List[ListPriceDetail]) -> int:
        """Inserta detalles de listas de precios en la base de datos."""
        pass

    @abstractmethod
    def insert_client_list_prices(self, client_list_prices: List[ClientListPrice]) -> int:
        """Inserta relaciones cliente-lista de precios en la base de datos."""
        pass

    @abstractmethod
    def insert_locations(self, locations: List[Location]) -> int:
        """Inserta ubicaciones en la base de datos."""
        pass

    @abstractmethod
    def insert_cobranzas(self, cobranzas: List[Cobranza]) -> int:
        """Inserta cobranzas en la base de datos."""
        pass

    @abstractmethod
    def insert_cobranza_details(self, cobranza_details: List[CobranzaDetail]) -> int:
        """Inserta detalles de cobranza en la base de datos."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Cierra la conexión con la base de datos SQLite."""
        pass
