"""
Tests unitarios para ExportService.
Demuestra el uso de mocks y testing de la capa de aplicación.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from decimal import Decimal

from src.application.export_service import ExportService
from src.domain.models import Cliente, Producto, ListaPrecio
from src.utils.exceptions import DatabaseConnectionError, ExportError


class TestExportService:
    """Suite de tests para ExportService."""

    @pytest.fixture
    def mock_repository(self):
        """Crea un mock del repositorio de datos."""
        return Mock()

    @pytest.fixture
    def mock_sqlite_builder(self):
        """Crea un mock del SQLite builder."""
        return Mock()

    @pytest.fixture
    def export_service(self, mock_repository, mock_sqlite_builder):
        """Crea una instancia de ExportService con mocks."""
        return ExportService(mock_repository, mock_sqlite_builder)

    @pytest.fixture
    def sample_cliente(self):
        """Cliente de ejemplo."""
        return Cliente(
            id=1,
            tenant_id=123,
            codigo="CLI001",
            nombre="Cliente Test"
        )

    @pytest.fixture
    def sample_producto(self):
        """Producto de ejemplo."""
        return Producto(
            id=1,
            tenant_id=123,
            codigo="PROD001",
            nombre="Producto Test",
            precio_base=Decimal("10.50")
        )

    @pytest.fixture
    def sample_lista_precio(self):
        """Lista de precio de ejemplo."""
        return ListaPrecio(
            id=1,
            tenant_id=123,
            producto_id=1,
            precio=Decimal("12.00")
        )

    def test_export_tenant_data_success(
        self,
        export_service,
        mock_repository,
        mock_sqlite_builder,
        sample_cliente,
        sample_producto,
        sample_lista_precio
    ):
        """Test de exportación exitosa."""
        # Arrange
        tenant_id = 123
        output_path = "/tmp/test.sqlite"

        mock_repository.get_clientes_by_tenant.return_value = [sample_cliente]
        mock_repository.get_productos_by_tenant.return_value = [sample_producto]
        mock_repository.get_listas_precios_by_tenant.return_value = [sample_lista_precio]

        with patch('os.path.getsize', return_value=1024):
            with patch('os.path.exists', return_value=True):
                # Act
                result = export_service.export_tenant_data(tenant_id, output_path)

        # Assert
        assert result.success is True
        assert result.file_path == output_path
        assert result.file_size == 1024
        assert result.records_exported['clientes'] == 1
        assert result.records_exported['productos'] == 1
        assert result.records_exported['listas_precios'] == 1

        # Verificar que se llamaron los métodos correctos
        mock_repository.connect.assert_called_once()
        mock_repository.get_clientes_by_tenant.assert_called_once_with(tenant_id)
        mock_repository.get_productos_by_tenant.assert_called_once_with(tenant_id)
        mock_repository.get_listas_precios_by_tenant.assert_called_once_with(tenant_id)

        mock_sqlite_builder.create_database.assert_called_once_with(output_path)
        mock_sqlite_builder.create_schema.assert_called_once()
        mock_sqlite_builder.insert_clientes.assert_called_once()
        mock_sqlite_builder.insert_productos.assert_called_once()
        mock_sqlite_builder.insert_listas_precios.assert_called_once()

    def test_export_tenant_data_no_data(
        self,
        export_service,
        mock_repository,
        mock_sqlite_builder
    ):
        """Test cuando no hay datos para exportar."""
        # Arrange
        tenant_id = 999
        output_path = "/tmp/test.sqlite"

        mock_repository.get_clientes_by_tenant.return_value = []
        mock_repository.get_productos_by_tenant.return_value = []
        mock_repository.get_listas_precios_by_tenant.return_value = []

        # Act
        result = export_service.export_tenant_data(tenant_id, output_path)

        # Assert
        assert result.success is False
        assert "No se encontraron datos" in result.error_message
        mock_sqlite_builder.create_database.assert_not_called()

    def test_export_tenant_data_connection_error(
        self,
        export_service,
        mock_repository,
        mock_sqlite_builder
    ):
        """Test cuando falla la conexión a la base de datos."""
        # Arrange
        tenant_id = 123
        output_path = "/tmp/test.sqlite"
        mock_repository.connect.side_effect = Exception("Connection failed")

        # Act
        result = export_service.export_tenant_data(tenant_id, output_path)

        # Assert
        assert result.success is False
        assert result.error_message is not None
        mock_repository.disconnect.assert_called_once()
