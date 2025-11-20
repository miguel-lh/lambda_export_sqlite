"""
Implementación del repositorio de datos para PostgreSQL.
Sigue el principio de Responsabilidad Única (SRP) de SOLID.

NOTA: Adapta los nombres de tablas y campos a tu esquema real de PostgreSQL.
"""
import logging
from typing import List, Optional

import psycopg2
from psycopg2.extras import RealDictCursor

from domain.interfaces import IDataRepository
from domain.models import (
    Customer, Product, BankAccount, ListPrice, ListPriceDetail,
    ClientListPrice, Location, Cobranza, CobranzaDetail
)

logger = logging.getLogger(__name__)


class PostgresRepository(IDataRepository):
    """
    Repositorio para acceder a datos en PostgreSQL.
    Implementa IDataRepository siguiendo el principio DIP.
    """

    def __init__(
        self,
        host: str,
        port: int,
        database: str,
        user: str,
        password: str
    ):
        """Inicializa el repositorio con las credenciales de conexión."""
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.connection: Optional[psycopg2.extensions.connection] = None

    def connect(self) -> None:
        """Establece conexión con PostgreSQL."""
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password,
                cursor_factory=RealDictCursor
            )
            logger.info(f"Conectado a PostgreSQL: {self.host}:{self.port}/{self.database}")
        except psycopg2.Error as e:
            logger.error(f"Error conectando a PostgreSQL: {e}")
            raise

    def disconnect(self) -> None:
        """Cierra la conexión con PostgreSQL."""
        if self.connection:
            self.connection.close()
            logger.info("Conexión a PostgreSQL cerrada")

    def get_customers_by_tenant(self, tenant_id: int) -> List[Customer]:
        """Obtiene todos los clientes de un tenant."""
        if not self.connection:
            raise RuntimeError("No hay conexión activa a PostgreSQL")

        # ADAPTA el nombre de la tabla y campos según tu esquema
        query = """
            SELECT
                id,
                slug,
                name,
                tel,
                email,
                code,
                sequence,
                format,
                type_sale,
                way_to_pay,
                street,
                ext_number,
                int_number,
                suburb,
                code_postal,
                city,
                state,
                country,
                lat,
                lng,
                geofence,
                sequence_times_from_1,
                sequence_times_up_to_1,
                sequence_times_from_2,
                sequence_times_up_to_2,
                sequence_times_from_3,
                sequence_times_up_to_3,
                is_pay_sun,
                is_pay_mon,
                is_pay_tues,
                is_pay_wed,
                is_pay_thurs,
                is_pay_fri,
                is_pay_sat,
                code_netsuit,
                credit_limit,
                checked,
                deuda
            FROM customer_customer  -- ADAPTA el nombre de la tabla
            WHERE parent_id = %s
            ORDER BY id
        """

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, (tenant_id,))
                rows = cursor.fetchall()

            customers = [
                Customer(
                    id=row['id'],
                    slug=row.get('slug'),
                    name=row.get('name'),
                    tel=row.get('tel'),
                    email=row.get('email'),
                    code=row.get('code'),
                    sequence=row.get('sequence'),
                    format=row.get('format'),
                    type_sale=row.get('type_sale'),
                    way_to_pay=row.get('way_to_pay'),
                    street=row.get('street'),
                    ext_number=row.get('ext_number'),
                    int_number=row.get('int_number'),
                    suburb=row.get('suburb'),
                    code_postal=row.get('code_postal'),
                    city=row.get('city'),
                    state=row.get('state'),
                    country=row.get('country'),
                    lat=row.get('lat'),
                    lng=row.get('lng'),
                    geofence=row.get('geofence'),
                    sequence_times_from1=row.get('sequence_times_from_1'),
                    sequence_times_up_to1=row.get('sequence_times_up_to_1'),
                    sequence_times_from2=row.get('sequence_times_from_2'),
                    sequence_times_up_to2=row.get('sequence_times_up_to_2'),
                    sequence_times_from3=row.get('sequence_times_from_3'),
                    sequence_times_up_to3=row.get('sequence_times_up_to_3'),
                    is_pay_sun=row.get('is_pay_sun'),
                    is_pay_mon=row.get('is_pay_mon'),
                    is_pay_tues=row.get('is_pay_tues'),
                    is_pay_wed=row.get('is_pay_wed'),
                    is_pay_thurs=row.get('is_pay_thurs'),
                    is_pay_fri=row.get('is_pay_fri'),
                    is_pay_sat=row.get('is_pay_sat'),
                    code_netsuit=row.get('code_netsuit'),
                    credit_limit=row.get('credit_limit'),
                    checked=row.get('checked'),
                    deuda=row.get('deuda')
                )
                for row in rows
            ]

            logger.info(f"Obtenidos {len(customers)} customers para tenant {tenant_id}")
            return customers

        except psycopg2.Error as e:
            logger.error(f"Error obteniendo customers: {e}")
            raise

    def get_products_by_tenant(self, tenant_id: int) -> List[Product]:
        """Obtiene todos los productos de un tenant."""
        if not self.connection:
            raise RuntimeError("No hay conexión activa a PostgreSQL")

        # ADAPTA el nombre de la tabla y campos según tu esquema
        query = """
            SELECT
                pp.id,
                pp.sku,
                pp.name,
                pp.description,
                pp.barcode,
                pp.type,
                cc.name as category,
                bb.name as brand
            FROM product_product as pp  -- ADAPTA el nombre de la tabla
            INNER JOIN category_category as cc ON pp.category_id = cc.id
            INNER JOIN brand_brand as bb ON pp.brand_id = bb.id
            WHERE pp.type IN (%s, %s, %s, %s, %s, %s)
            ORDER BY pp.id
        """

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, ('Ensamblaje', 'Artículo de inventario', 'Assembly', 'Inventory Item', 'Servicio', 'Service'))
                rows = cursor.fetchall()

            products = [
                Product(
                    id=row['id'],
                    sku=row.get('sku'),
                    name=row.get('name'),
                    description=row.get('description'),
                    bard_code=row.get('bard_code'),
                    type=row.get('type'),
                    brand=row.get('brand'),
                    category=row.get('category')
                )
                for row in rows
            ]

            logger.info(f"Obtenidos {len(products)} products para tenant {tenant_id}")
            return products

        except psycopg2.Error as e:
            logger.error(f"Error obteniendo products: {e}")
            raise

    def get_bank_accounts_by_tenant(self, tenant_id: int) -> List[BankAccount]:
        """Obtiene todas las cuentas bancarias de un tenant."""
        if not self.connection:
            raise RuntimeError("No hay conexión activa a PostgreSQL")

        # ADAPTA el nombre de la tabla y campos según tu esquema
        query = """
            SELECT
                ba.id,
                ba.name,
                b.name as bank_name,
                ba.number,
                baa.name as accounting_account_name
            FROM bank_accounts_bankaccounts as ba  -- ADAPTA el nombre de la tabla
            INNER JOIN bank_accounts_bank as b ON ba.bank_id = b.id
            INNER JOIN bank_accounts_accountingaccount baa on ba.accounting_account_id = baa.id
            ORDER BY id
        """

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query)
                rows = cursor.fetchall()

            bank_accounts = [
                BankAccount(
                    id=row['id'],
                    name=row.get('name'),
                    bank_name=row.get('bank_name'),
                    number=row.get('number'),
                    accounting_account_name=row.get('accounting_account_name')
                )
                for row in rows
            ]

            logger.info(f"Obtenidas {len(bank_accounts)} bank accounts para tenant {tenant_id}")
            return bank_accounts

        except psycopg2.Error as e:
            logger.error(f"Error obteniendo bank accounts: {e}")
            raise

    def get_list_prices_by_tenant(self, tenant_id: int) -> List[ListPrice]:
        """Obtiene todas las listas de precios de un tenant."""
        if not self.connection:
            raise RuntimeError("No hay cnexión activa a PostgreSQL")

        # ADAPTA el nombre de la tabla y campos según tu esquema
        query = """
            SELECT DISTINCT
                l.id,
                l.name,
                l.max,
                l.min,
                l.customer_sync_id as customer_sync
            FROM list_price_pricelist as l -- ADAPTA el nombre de la tabla
            INNER JOIN customer_customer_list_price as clp ON l.id = clp.pricelist_id
            INNER JOIN customer_customer as cc ON clp.customer_id = cc.id
            WHERE  CC.parent_id= %s
            ORDER BY id
        """

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, (tenant_id,))
                rows = cursor.fetchall()

            list_prices = [
                ListPrice(
                    id=row['id'],
                    name=row.get('name'),
                    max=row.get('max'),
                    min=row.get('min'),
                    customer_sync=row.get('customer_sync')
                )
                for row in rows
            ]

            logger.info(f"Obtenidas {len(list_prices)} list prices para tenant {tenant_id}")
            return list_prices

        except psycopg2.Error as e:
            logger.error(f"Error obteniendo list prices: {e}")
            raise

    def get_list_price_details_by_tenant(self, tenant_id: int) -> List[ListPriceDetail]:
        """Obtiene todos los detalles de listas de precios de un tenant."""
        if not self.connection:
            raise RuntimeError("No hay conexión activa a PostgreSQL")

        # ADAPTA el nombre de la tabla y campos según tu esquema
        query = """
            SELECT DISTINCT
                lpd.id,
                lpd.price_list_id as id_price_list,
                lpd.product_id as id_product,
                lpd.price
            FROM list_price_pricelistdetail lpd  -- ADAPTA el nombre de la tabla
            INNER JOIN customer_customer_list_price as clp ON lpd.price_list_id = clp.pricelist_id
            INNER JOIN customer_customer as cc ON clp.customer_id = cc.id
            WHERE cc.parent_id = %s
            ORDER BY lpd.id
        """

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, (tenant_id,))
                rows = cursor.fetchall()

            list_price_details = [
                ListPriceDetail(
                    id=row['id'],
                    id_price_list=row['id_price_list'],
                    id_product=row['id_product'],
                    price=row.get('price')
                )
                for row in rows
            ]

            logger.info(f"Obtenidos {len(list_price_details)} list price details para tenant {tenant_id}")
            return list_price_details

        except psycopg2.Error as e:
            logger.error(f"Error obteniendo list price details: {e}")
            raise

    def get_client_list_prices_by_tenant(self, tenant_id: int) -> List[ClientListPrice]:
        """Obtiene todas las relaciones cliente-lista de precios de un tenant."""
        if not self.connection:
            raise RuntimeError("No hay conexión activa a PostgreSQL")

        # ADAPTA el nombre de la tabla y campos según tu esquema
        query = """
            SELECT
                clp.id,
                clp.customer_id as id_client,
                clp.pricelist_id as id_list_price
            FROM customer_customer_list_price as clp  -- ADAPTA el nombre de la tabla
            INNER JOIN customer_customer as cc ON clp.customer_id = cc.id
            WHERE cc.parent_id = %s
            ORDER BY clp.id
        """

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, (tenant_id,))
                rows = cursor.fetchall()

            client_list_prices = [
                ClientListPrice(
                    id=row['id'],
                    id_client=row['id_client'],
                    id_list_price=row['id_list_price']
                )
                for row in rows
            ]

            logger.info(f"Obtenidas {len(client_list_prices)} client list prices para tenant {tenant_id}")
            return client_list_prices

        except psycopg2.Error as e:
            logger.error(f"Error obteniendo client list prices: {e}")
            raise

    def get_locations_by_tenant(self, tenant_id: int) -> List[Location]:
        """Obtiene todas las ubicaciones de un tenant."""
        if not self.connection:
            raise RuntimeError("No hay conexión activa a PostgreSQL")

        # ADAPTA el nombre de la tabla y campos según tu esquema
        query = """
            SELECT
                id,
                slug,
                name,
                tel,
                email,
                code,
                sequence,
                format,
                zone_id as zone,
                "using" as use,
                category_id as category,
                type_location_id as type_location,
                street,
                ext_number,
                int_number,
                suburb,
                code_postal,
                city,
                state,
                country,
                lat,
                lng,
                geofence,
                sequence_times_from_1,
                sequence_times_up_to_1,
                sequence_times_from_2,
                sequence_times_up_to_2,
                sequence_times_from_3,
                sequence_times_up_to_3,
                is_pay_sun,
                is_pay_mon,
                is_pay_tues,
                is_pay_wed,
                is_pay_thurs,
                is_pay_fri,
                is_pay_sat,
                seller,
                checked
            FROM location_location  -- ADAPTA el nombre de la tabla
            WHERE parent_id = %s
            ORDER BY id
        """

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, (tenant_id,))
                rows = cursor.fetchall()

            locations = [
                Location(
                    id=row['id'],
                    slug=row.get('slug'),
                    name=row.get('name'),
                    tel=row.get('tel'),
                    email=row.get('email'),
                    code=row.get('code'),
                    sequence=row.get('sequence'),
                    format=row.get('format'),
                    zone=row.get('zone'),
                    use=row.get('use'),
                    category=row.get('category'),
                    type_location=row.get('type_location'),
                    street=row.get('street'),
                    ext_number=row.get('ext_number'),
                    int_number=row.get('int_number'),
                    suburb=row.get('suburb'),
                    code_postal=row.get('code_postal'),
                    city=row.get('city'),
                    state=row.get('state'),
                    country=row.get('country'),
                    lat=row.get('lat'),
                    lng=row.get('lng'),
                    geofence=row.get('geofence'),
                    sequence_times_from1=row.get('sequence_times_from1'),
                    sequence_times_up_to1=row.get('sequence_times_up_to1'),
                    sequence_times_from2=row.get('sequence_times_from2'),
                    sequence_times_up_to2=row.get('sequence_times_up_to2'),
                    sequence_times_from3=row.get('sequence_times_from3'),
                    sequence_times_up_to3=row.get('sequence_times_up_to3'),
                    is_pay_sun=row.get('is_pay_sun'),
                    is_pay_mon=row.get('is_pay_mon'),
                    is_pay_tues=row.get('is_pay_tues'),
                    is_pay_wed=row.get('is_pay_wed'),
                    is_pay_thurs=row.get('is_pay_thurs'),
                    is_pay_fri=row.get('is_pay_fri'),
                    is_pay_sat=row.get('is_pay_sat'),
                    seller=row.get('seller'),
                    checked=row.get('checked')
                )
                for row in rows
            ]

            logger.info(f"Obtenidas {len(locations)} locations para tenant {tenant_id}")
            return locations

        except psycopg2.Error as e:
            logger.error(f"Error obteniendo locations: {e}")
            raise

    def get_cobranzas_by_tenant(self, tenant_id: int) -> List[Cobranza]:
        """Obtiene todas las cobranzas de un tenant."""
        if not self.connection:
            raise RuntimeError("No hay conexión activa a PostgreSQL")

        # ADAPTA el nombre de la tabla y campos según tu esquema
        query = """
            SELECT
                cob.id,
                cob.customer_id as id_client,
                cob.bill_number,
                cob.total,
                cob.issue,
                cob.validity
            FROM cobranza_cobranza cob  -- ADAPTA el nombre de la tabla
            INNER JOIN customer_customer c ON cob.customer_id = c.id
            WHERE c.parent_id = %s
            ORDER BY cob.id
        """

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, (tenant_id,))
                rows = cursor.fetchall()

            cobranzas = [
                Cobranza(
                    id=row['id'],
                    id_client=row['id_client'],
                    bill_number=row.get('bill_number'),
                    total=row.get('total'),
                    issue=row.get('issue'),
                    validity=row.get('validity')
                )
                for row in rows
            ]

            logger.info(f"Obtenidas {len(cobranzas)} cobranzas para tenant {tenant_id}")
            return cobranzas

        except psycopg2.Error as e:
            logger.error(f"Error obteniendo cobranzas: {e}")
            raise

    def get_cobranza_details_by_tenant(self, tenant_id: int) -> List[CobranzaDetail]:
        """Obtiene todos los detalles de cobranza de un tenant."""
        if not self.connection:
            raise RuntimeError("No hay conexión activa a PostgreSQL")

        # ADAPTA el nombre de la tabla y campos según tu esquema
        query = """
            SELECT
                cd.id,
                cd.cobranza_id as id_cobranza,
                cd.product_id as id_product,
                cd.amount,
                cd.price
            FROM cobranza_cobranzadetail cd  -- ADAPTA el nombre de la tabla
            INNER JOIN cobranza_cobranza cob ON cd.cobranza_id = cob.id
            INNER JOIN customer_customer c ON cob.customer_id = c.id
            WHERE c.parent_id = %s
            ORDER BY cd.id
        """

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, (tenant_id,))
                rows = cursor.fetchall()

            cobranza_details = [
                CobranzaDetail(
                    id=row['id'],
                    id_cobranza=row['id_cobranza'],
                    id_product=row['id_product'],
                    amount=row.get('amount'),
                    price=row.get('price')
                )
                for row in rows
            ]

            logger.info(f"Obtenidos {len(cobranza_details)} cobranza details para tenant {tenant_id}")
            return cobranza_details

        except psycopg2.Error as e:
            logger.error(f"Error obteniendo cobranza details: {e}")
            raise
