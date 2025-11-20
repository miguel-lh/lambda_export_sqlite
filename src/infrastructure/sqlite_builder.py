"""
Constructor de archivos SQLite.
Sigue el principio de Responsabilidad Única (SRP) de SOLID.
"""
import logging
import sqlite3
from typing import List, Optional

from src.domain.interfaces import ISQLiteBuilder
from src.domain.models import (
    Customer, Product, BankAccount, ListPrice, ListPriceDetail,
    ClientListPrice, Location, Cobranza, CobranzaDetail
)

logger = logging.getLogger(__name__)


class SQLiteBuilder(ISQLiteBuilder):
    """
    Constructor de bases de datos SQLite.
    Implementa ISQLiteBuilder siguiendo el principio DIP.
    """

    def __init__(self):
        """Inicializa el constructor SQLite."""
        self.connection: Optional[sqlite3.Connection] = None
        self.file_path: Optional[str] = None

    def create_database(self, file_path: str) -> None:
        """
        Crea una nueva base de datos SQLite.

        Args:
            file_path: Ruta donde crear el archivo SQLite
        """
        try:
            self.file_path = file_path
            self.connection = sqlite3.connect(file_path)
            logger.info(f"Base de datos SQLite creada: {file_path}")
        except sqlite3.Error as e:
            logger.error(f"Error creando base de datos SQLite: {e}")
            raise

    def create_schema(self) -> None:
        """Crea el esquema de tablas en la base de datos."""
        if not self.connection:
            raise RuntimeError("No hay conexión activa a SQLite")

        try:
            cursor = self.connection.cursor()

            # Tabla clientes
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Customer (
                    Id INTEGER PRIMARY KEY,
                    Slug TEXT,
                    Name TEXT,
                    Tel TEXT,
                    Email TEXT,
                    Code TEXT,
                    Sequence INTEGER,
                    Format TEXT,
                    TypeSale TEXT,
                    WayToPay TEXT,
                    Street TEXT,
                    ExtNumber TEXT,
                    IntNumber TEXT,
                    Suburb TEXT,
                    CodePostal TEXT,
                    City TEXT,
                    State TEXT,
                    Country TEXT,
                    Lat TEXT,
                    Lng TEXT,
                    Geofence TEXT,
                    SequenceTimesFrom1 LONG,
                    SequenceTimesUpTo1 LONG,
                    SequenceTimesFrom2 LONG,
                    SequenceTimesUpTo2 LONG,
                    SequenceTimesFrom3 LONG,
                    SequenceTimesUpTo3 LONG,
                    IsPaySun BOOLEAN,
                    IsPayMon BOOLEAN,
                    IsPayTues BOOLEAN,
                    IsPayWed BOOLEAN,
                    IsPayThurs BOOLEAN,
                    IsPayFri BOOLEAN,
                    IsPaySat BOOLEAN,
                    CodeNetsuit TEXT,
                    CreditLimit TEXT,
                    Checked BOOLEAN,
                    Deuda TEXT
                )
            """)

            # Tabla producto
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Product (
                    Id INTEGER PRIMARY KEY,
                    Sku TEXT,
                    Name TEXT,
                    Description TEXT,
                    BardCode TEXT,
                    Type TEXT,
                    Brand TEXT,
                    Category TEXT
                )
            """)

            # Tabla Cuentas bancarias
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS BankAccount (
                    Id INTEGER PRIMARY KEY,
                    Name TEXT,
                    BankName TEXT,
                    Number TEXT,
                    AccountingAccountName TEXT
                )
            """)

            # Tabla listas_precios
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ListPrice (
                    Id INTEGER,
                    Name TEXT,
                    Max TEXT,
                    Min TEXT,
                    CustomerSync INTEGER
                )
            """)

            # Tabla Productos - Lista de precios
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ListPriceDetail (
                    Id INTEGER PRIMARY KEY,
                    IdPriceList INTEGER,
                    IdProduct INTEGER,
                    Price TEXT,
                    FOREIGN KEY (IdProduct) REFERENCES Product (Id)
                )
            """)

            # Tabla Clientes - Lista de precios
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ClientListPrice (
                    Id INTEGER PRIMARY KEY,
                    IdClient INTEGER,
                    IdListPrice INTEGER,
                    FOREIGN KEY (IdClient) REFERENCES Customer (Id)
                )
            """)

            # Tabla Ubicaciones
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Location (
                    Id INTEGER PRIMARY KEY,
                    Slug TEXT,
                    Name TEXT,
                    Tel TEXT,
                    Email TEXT,
                    Code TEXT,
                    Sequence INTEGER,
                    Format TEXT,
                    Zone TEXT,
                    Use TEXT,
                    Category TEXT,
                    TypeLocation TEXT,
                    Street TEXT,
                    ExtNumber TEXT,
                    IntNumber TEXT,
                    Suburb TEXT,
                    CodePostal TEXT,
                    City TEXT,
                    State TEXT,
                    Country TEXT,
                    Lat TEXT,
                    Lng TEXT,
                    Geofence TEXT,
                    SequenceTimesFrom1 LONG,
                    SequenceTimesUpTo1 LONG,
                    SequenceTimesFrom2 LONG,
                    SequenceTimesUpTo2 LONG,
                    SequenceTimesFrom3 LONG,
                    SequenceTimesUpTo3 LONG,
                    IsPaySun BOOLEAN,
                    IsPayMon BOOLEAN,
                    IsPayTues BOOLEAN,
                    IsPayWed BOOLEAN,
                    IsPayThurs BOOLEAN,
                    IsPayFri BOOLEAN,
                    IsPaySat BOOLEAN,
                    Seller TEXT,
                    Checked BOOLEAN
                )
            """)

            # Tabla Cobranza
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Cobranza (
                    Id INTEGER PRIMARY KEY,
                    IdClient INTEGER,
                    BillNumber TEXT,
                    Total TEXT,
                    Issue TEXT,
                    Validity TEXT,
                    FOREIGN KEY (IdClient) REFERENCES Customer (Id)
                )
            """)

            # Tabla Detalle de cobranza
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS CobranzaDetail (
                    Id INTEGER PRIMARY KEY,
                    IdCobranza INTEGER,
                    IdProduct INTEGER,
                    Amount TEXT,
                    Price TEXT,
                    FOREIGN KEY (IdCobranza) REFERENCES Cobranza (Id),
                    FOREIGN KEY (IdProduct) REFERENCES Product (Id)
                )
            """)
            
            
            # Crear índices para mejorar rendimiento
            # cursor.execute("CREATE INDEX IF NOT EXISTS idx_clientes_tenant ON clientes(tenant_id)")
            # cursor.execute("CREATE INDEX IF NOT EXISTS idx_producto_tenant ON producto(tenant_id)")
            # cursor.execute("CREATE INDEX IF NOT EXISTS idx_listas_tenant ON listas_precios(tenant_id)")
            # cursor.execute("CREATE INDEX IF NOT EXISTS idx_listas_producto ON listas_precios(producto_id)")
            # cursor.execute("CREATE INDEX IF NOT EXISTS idx_listas_cliente ON listas_precios(cliente_id)")

            self.connection.commit()
            logger.info("Esquema de base de datos creado exitosamente")

        except sqlite3.Error as e:
            logger.error(f"Error creando esquema: {e}")
            raise

    def insert_customers(self, customers: List[Customer]) -> int:
        """Inserta clientes en la base de datos."""
        if not self.connection:
            raise RuntimeError("No hay conexión activa a SQLite")

        if not customers:
            logger.warning("No hay customers para insertar")
            return 0

        try:
            cursor = self.connection.cursor()

            for customer in customers:
                cursor.execute("""
                    INSERT INTO Customer (
                        Id, Slug, Name, Tel, Email, Code, Sequence, Format,
                        TypeSale, WayToPay, Street, ExtNumber, IntNumber, Suburb,
                        CodePostal, City, State, Country, Lat, Lng, Geofence,
                        SequenceTimesFrom1, SequenceTimesUpTo1, SequenceTimesFrom2,
                        SequenceTimesUpTo2, SequenceTimesFrom3, SequenceTimesUpTo3,
                        IsPaySun, IsPayMon, IsPayTues, IsPayWed, IsPayThurs, IsPayFri,
                        IsPaySat, CodeNetsuit, CreditLimit, Checked, Deuda
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    customer.id,
                    customer.slug,
                    customer.name,
                    customer.tel,
                    customer.email,
                    customer.code,
                    customer.sequence,
                    customer.format,
                    customer.type_sale,
                    customer.way_to_pay,
                    customer.street,
                    customer.ext_number,
                    customer.int_number,
                    customer.suburb,
                    customer.code_postal,
                    customer.city,
                    customer.state,
                    customer.country,
                    customer.lat,
                    customer.lng,
                    customer.geofence,
                    customer.sequence_times_from1,
                    customer.sequence_times_up_to1,
                    customer.sequence_times_from2,
                    customer.sequence_times_up_to2,
                    customer.sequence_times_from3,
                    customer.sequence_times_up_to3,
                    1 if customer.is_pay_sun else 0,
                    1 if customer.is_pay_mon else 0,
                    1 if customer.is_pay_tues else 0,
                    1 if customer.is_pay_wed else 0,
                    1 if customer.is_pay_thurs else 0,
                    1 if customer.is_pay_fri else 0,
                    1 if customer.is_pay_sat else 0,
                    customer.code_netsuit,
                    customer.credit_limit,
                    1 if customer.checked else 0,
                    customer.deuda
                ))

            self.connection.commit()
            count = len(customers)
            logger.info(f"Insertados {count} customers")
            return count

        except sqlite3.Error as e:
            logger.error(f"Error insertando customers: {e}")
            self.connection.rollback()
            raise

    def insert_products(self, products: List[Product]) -> int:
        """Inserta productos en la base de datos."""
        if not self.connection:
            raise RuntimeError("No hay conexión activa a SQLite")

        if not products:
            logger.warning("No hay products para insertar")
            return 0

        try:
            cursor = self.connection.cursor()

            for product in products:
                cursor.execute("""
                    INSERT INTO Product (
                        Id, Sku, Name, Description, BardCode, Type, Brand, Category
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    product.id,
                    product.sku,
                    product.name,
                    product.description,
                    product.bard_code,
                    product.type,
                    product.brand,
                    product.category
                ))

            self.connection.commit()
            count = len(products)
            logger.info(f"Insertados {count} products")
            return count

        except sqlite3.Error as e:
            logger.error(f"Error insertando products: {e}")
            self.connection.rollback()
            raise

    def insert_bank_accounts(self, bank_accounts: List[BankAccount]) -> int:
        """Inserta cuentas bancarias en la base de datos."""
        if not self.connection:
            raise RuntimeError("No hay conexión activa a SQLite")

        if not bank_accounts:
            logger.warning("No hay bank accounts para insertar")
            return 0

        try:
            cursor = self.connection.cursor()

            for account in bank_accounts:
                cursor.execute("""
                    INSERT INTO BankAccount (
                        Id, Name, BankName, Number, AccountingAccountName
                    ) VALUES (?, ?, ?, ?, ?)
                """, (
                    account.id,
                    account.name,
                    account.bank_name,
                    account.number,
                    account.accounting_account_name
                ))

            self.connection.commit()
            count = len(bank_accounts)
            logger.info(f"Insertados {count} bank accounts")
            return count

        except sqlite3.Error as e:
            logger.error(f"Error insertando bank accounts: {e}")
            self.connection.rollback()
            raise

    def insert_list_prices(self, list_prices: List[ListPrice]) -> int:
        """Inserta listas de precios en la base de datos."""
        if not self.connection:
            raise RuntimeError("No hay conexión activa a SQLite")

        if not list_prices:
            logger.warning("No hay list prices para insertar")
            return 0

        try:
            cursor = self.connection.cursor()

            for list_price in list_prices:
                cursor.execute("""
                    INSERT INTO ListPrice (
                        Id, Name, Max, Min, CustomerSync
                    ) VALUES (?, ?, ?, ?, ?)
                """, (
                    list_price.id,
                    list_price.name,
                    list_price.max,
                    list_price.min,
                    list_price.customer_sync
                ))

            self.connection.commit()
            count = len(list_prices)
            logger.info(f"Insertados {count} list prices")
            return count

        except sqlite3.Error as e:
            logger.error(f"Error insertando list prices: {e}")
            self.connection.rollback()
            raise

    def insert_list_price_details(self, list_price_details: List[ListPriceDetail]) -> int:
        """Inserta detalles de listas de precios en la base de datos."""
        if not self.connection:
            raise RuntimeError("No hay conexión activa a SQLite")

        if not list_price_details:
            logger.warning("No hay list price details para insertar")
            return 0

        try:
            cursor = self.connection.cursor()

            for detail in list_price_details:
                cursor.execute("""
                    INSERT INTO ListPriceDetail (
                        Id, IdPriceList, IdProduct, Price
                    ) VALUES (?, ?, ?, ?)
                """, (
                    detail.id,
                    detail.id_price_list,
                    detail.id_product,
                    detail.price
                ))

            self.connection.commit()
            count = len(list_price_details)
            logger.info(f"Insertados {count} list price details")
            return count

        except sqlite3.Error as e:
            logger.error(f"Error insertando list price details: {e}")
            self.connection.rollback()
            raise

    def insert_client_list_prices(self, client_list_prices: List[ClientListPrice]) -> int:
        """Inserta relaciones cliente-lista de precios en la base de datos."""
        if not self.connection:
            raise RuntimeError("No hay conexión activa a SQLite")

        if not client_list_prices:
            logger.warning("No hay client list prices para insertar")
            return 0

        try:
            cursor = self.connection.cursor()

            for client_list_price in client_list_prices:
                cursor.execute("""
                    INSERT INTO ClientListPrice (
                        Id, IdClient, IdListPrice
                    ) VALUES (?, ?, ?)
                """, (
                    client_list_price.id,
                    client_list_price.id_client,
                    client_list_price.id_list_price
                ))

            self.connection.commit()
            count = len(client_list_prices)
            logger.info(f"Insertados {count} client list prices")
            return count

        except sqlite3.Error as e:
            logger.error(f"Error insertando client list prices: {e}")
            self.connection.rollback()
            raise

    def insert_locations(self, locations: List[Location]) -> int:
        """Inserta ubicaciones en la base de datos."""
        if not self.connection:
            raise RuntimeError("No hay conexión activa a SQLite")

        if not locations:
            logger.warning("No hay locations para insertar")
            return 0

        try:
            cursor = self.connection.cursor()

            for location in locations:
                cursor.execute("""
                    INSERT INTO Location (
                        Id, Slug, Name, Tel, Email, Code, Sequence, Format, Zone, Use,
                        Category, TypeLocation, Street, ExtNumber, IntNumber, Suburb,
                        CodePostal, City, State, Country, Lat, Lng, Geofence,
                        SequenceTimesFrom1, SequenceTimesUpTo1, SequenceTimesFrom2,
                        SequenceTimesUpTo2, SequenceTimesFrom3, SequenceTimesUpTo3,
                        IsPaySun, IsPayMon, IsPayTues, IsPayWed, IsPayThurs, IsPayFri,
                        IsPaySat, Seller, Checked
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    location.id,
                    location.slug,
                    location.name,
                    location.tel,
                    location.email,
                    location.code,
                    location.sequence,
                    location.format,
                    location.zone,
                    location.use,
                    location.category,
                    location.type_location,
                    location.street,
                    location.ext_number,
                    location.int_number,
                    location.suburb,
                    location.code_postal,
                    location.city,
                    location.state,
                    location.country,
                    location.lat,
                    location.lng,
                    location.geofence,
                    location.sequence_times_from1,
                    location.sequence_times_up_to1,
                    location.sequence_times_from2,
                    location.sequence_times_up_to2,
                    location.sequence_times_from3,
                    location.sequence_times_up_to3,
                    1 if location.is_pay_sun else 0,
                    1 if location.is_pay_mon else 0,
                    1 if location.is_pay_tues else 0,
                    1 if location.is_pay_wed else 0,
                    1 if location.is_pay_thurs else 0,
                    1 if location.is_pay_fri else 0,
                    1 if location.is_pay_sat else 0,
                    location.seller,
                    1 if location.checked else 0
                ))

            self.connection.commit()
            count = len(locations)
            logger.info(f"Insertados {count} locations")
            return count

        except sqlite3.Error as e:
            logger.error(f"Error insertando locations: {e}")
            self.connection.rollback()
            raise

    def insert_cobranzas(self, cobranzas: List[Cobranza]) -> int:
        """Inserta cobranzas en la base de datos."""
        if not self.connection:
            raise RuntimeError("No hay conexión activa a SQLite")

        if not cobranzas:
            logger.warning("No hay cobranzas para insertar")
            return 0

        try:
            cursor = self.connection.cursor()

            for cobranza in cobranzas:
                cursor.execute("""
                    INSERT INTO Cobranza (
                        Id, IdClient, BillNumber, Total, Issue, Validity
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    cobranza.id,
                    cobranza.id_client,
                    cobranza.bill_number,
                    cobranza.total,
                    cobranza.issue,
                    cobranza.validity
                ))

            self.connection.commit()
            count = len(cobranzas)
            logger.info(f"Insertados {count} cobranzas")
            return count

        except sqlite3.Error as e:
            logger.error(f"Error insertando cobranzas: {e}")
            self.connection.rollback()
            raise

    def insert_cobranza_details(self, cobranza_details: List[CobranzaDetail]) -> int:
        """Inserta detalles de cobranza en la base de datos."""
        if not self.connection:
            raise RuntimeError("No hay conexión activa a SQLite")

        if not cobranza_details:
            logger.warning("No hay cobranza details para insertar")
            return 0

        try:
            cursor = self.connection.cursor()

            for detail in cobranza_details:
                cursor.execute("""
                    INSERT INTO CobranzaDetail (
                        Id, IdCobranza, IdProduct, Amount, Price
                    ) VALUES (?, ?, ?, ?, ?)
                """, (
                    detail.id,
                    detail.id_cobranza,
                    detail.id_product,
                    detail.amount,
                    detail.price
                ))

            self.connection.commit()
            count = len(cobranza_details)
            logger.info(f"Insertados {count} cobranza details")
            return count

        except sqlite3.Error as e:
            logger.error(f"Error insertando cobranza details: {e}")
            self.connection.rollback()
            raise

    def close(self) -> None:
        """Cierra la conexión con la base de datos SQLite."""
        if self.connection:
            self.connection.close()
            logger.info("Conexión SQLite cerrada")
