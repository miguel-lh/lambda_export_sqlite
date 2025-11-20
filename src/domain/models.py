"""
Modelos de dominio para la aplicación.
Representa las entidades del negocio sin dependencias de infraestructura.
"""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Customer:
    """Modelo de dominio para Customer (Cliente)."""

    id: int
    slug: Optional[str] = None
    name: Optional[str] = None
    tel: Optional[str] = None
    email: Optional[str] = None
    code: Optional[str] = None
    sequence: Optional[int] = None
    format: Optional[str] = None
    type_sale: Optional[str] = None
    way_to_pay: Optional[str] = None
    street: Optional[str] = None
    ext_number: Optional[str] = None
    int_number: Optional[str] = None
    suburb: Optional[str] = None
    code_postal: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    lat: Optional[str] = None
    lng: Optional[str] = None
    geofence: Optional[str] = None
    sequence_times_from1: Optional[int] = None
    sequence_times_up_to1: Optional[int] = None
    sequence_times_from2: Optional[int] = None
    sequence_times_up_to2: Optional[int] = None
    sequence_times_from3: Optional[int] = None
    sequence_times_up_to3: Optional[int] = None
    is_pay_sun: Optional[bool] = None
    is_pay_mon: Optional[bool] = None
    is_pay_tues: Optional[bool] = None
    is_pay_wed: Optional[bool] = None
    is_pay_thurs: Optional[bool] = None
    is_pay_fri: Optional[bool] = None
    is_pay_sat: Optional[bool] = None
    code_netsuit: Optional[str] = None
    credit_limit: Optional[str] = None
    checked: Optional[bool] = None
    deuda: Optional[str] = None


@dataclass
class Product:
    """Modelo de dominio para Product (Producto)."""

    id: int
    sku: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    bard_code: Optional[str] = None
    type: Optional[str] = None
    brand: Optional[str] = None
    category: Optional[str] = None


@dataclass
class BankAccount:
    """Modelo de dominio para BankAccount (Cuenta Bancaria)."""

    id: int
    name: Optional[str] = None
    bank_name: Optional[str] = None
    number: Optional[str] = None
    accounting_account_name: Optional[str] = None


@dataclass
class ListPrice:
    """Modelo de dominio para ListPrice (Lista de Precios)."""

    id: int
    name: Optional[str] = None
    max: Optional[str] = None
    min: Optional[str] = None
    customer_sync: Optional[int] = None


@dataclass
class ListPriceDetail:
    """Modelo de dominio para ListPriceDetail (Detalle de Lista de Precios)."""

    id: int
    id_price_list: int
    id_product: int
    price: Optional[str] = None


@dataclass
class ClientListPrice:
    """Modelo de dominio para ClientListPrice (Cliente - Lista de Precios)."""

    id: int
    id_client: int
    id_list_price: int


@dataclass
class Location:
    """Modelo de dominio para Location (Ubicación)."""

    id: int
    slug: Optional[str] = None
    name: Optional[str] = None
    tel: Optional[str] = None
    email: Optional[str] = None
    code: Optional[str] = None
    sequence: Optional[int] = None
    format: Optional[str] = None
    zone: Optional[str] = None
    use: Optional[str] = None
    category: Optional[str] = None
    type_location: Optional[str] = None
    street: Optional[str] = None
    ext_number: Optional[str] = None
    int_number: Optional[str] = None
    suburb: Optional[str] = None
    code_postal: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    lat: Optional[str] = None
    lng: Optional[str] = None
    geofence: Optional[str] = None
    sequence_times_from1: Optional[int] = None
    sequence_times_up_to1: Optional[int] = None
    sequence_times_from2: Optional[int] = None
    sequence_times_up_to2: Optional[int] = None
    sequence_times_from3: Optional[int] = None
    sequence_times_up_to3: Optional[int] = None
    is_pay_sun: Optional[bool] = None
    is_pay_mon: Optional[bool] = None
    is_pay_tues: Optional[bool] = None
    is_pay_wed: Optional[bool] = None
    is_pay_thurs: Optional[bool] = None
    is_pay_fri: Optional[bool] = None
    is_pay_sat: Optional[bool] = None
    seller: Optional[str] = None
    checked: Optional[bool] = None


@dataclass
class Cobranza:
    """Modelo de dominio para Cobranza."""

    id: int
    id_client: int
    bill_number: Optional[str] = None
    total: Optional[str] = None
    issue: Optional[str] = None
    validity: Optional[str] = None


@dataclass
class CobranzaDetail:
    """Modelo de dominio para CobranzaDetail (Detalle de Cobranza)."""

    id: int
    id_cobranza: int
    id_product: int
    amount: Optional[str] = None
    price: Optional[str] = None


@dataclass
class ExportResult:
    """Resultado de la operación de exportación."""

    success: bool
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    records_exported: dict = field(default_factory=dict)
    error_message: Optional[str] = None
    execution_time_ms: Optional[int] = None

    def to_dict(self) -> dict:
        """Convierte el resultado a diccionario."""
        return {
            'success': self.success,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'records_exported': self.records_exported,
            'error_message': self.error_message,
            'execution_time_ms': self.execution_time_ms
        }
