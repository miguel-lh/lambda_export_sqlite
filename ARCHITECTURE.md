# Arquitectura del Proyecto

## Diagrama de Capas

```
┌─────────────────────────────────────────────────────────────┐
│                    API Gateway / Lambda                      │
│                      (handler.py)                            │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  Application Layer                           │
│              (export_service.py)                             │
│  • Orquestación de operaciones                              │
│  • Lógica de negocio                                        │
│  • Manejo de errores                                        │
└─────────────┬────────────────────────┬──────────────────────┘
              │                        │
              ▼                        ▼
┌─────────────────────────┐  ┌─────────────────────────┐
│  Infrastructure Layer   │  │  Infrastructure Layer   │
│ (postgres_repository.py)│  │   (sqlite_builder.py)   │
│  • Conexión a DB        │  │  • Creación SQLite      │
│  • Queries              │  │  • Esquema              │
│  • Mapeo a modelos      │  │  • Inserción datos      │
└─────────────┬───────────┘  └───────────┬─────────────┘
              │                          │
              ▼                          ▼
┌─────────────────────────────────────────────────────────────┐
│                      Domain Layer                            │
│              (models.py, interfaces.py)                      │
│  • Entidades de negocio (Cliente, Producto, ListaPrecio)    │
│  • Interfaces (IDataRepository, ISQLiteBuilder)             │
│  • Modelos de resultado (ExportResult)                      │
└─────────────────────────────────────────────────────────────┘
```

## Flujo de Datos

```
1. Request HTTP
   ↓
2. API Gateway → Lambda Handler (handler.py)
   ↓
3. Extracción y validación de tenant_id
   ↓
4. Creación de dependencias (Repository, Builder)
   ↓
5. ExportService.export_tenant_data()
   ├─→ PostgresRepository.connect()
   ├─→ PostgresRepository.get_clientes_by_tenant()
   ├─→ PostgresRepository.get_productos_by_tenant()
   ├─→ PostgresRepository.get_listas_precios_by_tenant()
   ├─→ SQLiteBuilder.create_database()
   ├─→ SQLiteBuilder.create_schema()
   ├─→ SQLiteBuilder.insert_clientes()
   ├─→ SQLiteBuilder.insert_productos()
   ├─→ SQLiteBuilder.insert_listas_precios()
   └─→ Return ExportResult
   ↓
6. Leer archivo SQLite
   ↓
7. Codificar a Base64
   ↓
8. Response HTTP con archivo
```

## Principios SOLID Implementados

### 1. Single Responsibility Principle (SRP)

Cada clase tiene una única responsabilidad:

- **PostgresRepository**: Responsable únicamente de acceder a datos en PostgreSQL
- **SQLiteBuilder**: Responsable únicamente de construir archivos SQLite
- **ExportService**: Responsable únicamente de orquestar el proceso de exportación
- **Settings**: Responsable únicamente de gestionar la configuración

### 2. Open/Closed Principle (OCP)

El código es abierto a extensión pero cerrado a modificación:

- Nuevas fuentes de datos pueden agregarse implementando `IDataRepository`
- Nuevos formatos de exportación pueden agregarse implementando una nueva interfaz
- No se requiere modificar código existente para agregar funcionalidades

### 3. Liskov Substitution Principle (LSP)

Las implementaciones son intercambiables:

- Cualquier implementación de `IDataRepository` puede reemplazar a `PostgresRepository`
- Cualquier implementación de `ISQLiteBuilder` puede reemplazar a `SQLiteBuilder`
- El `ExportService` funciona con cualquier implementación que cumpla el contrato

### 4. Interface Segregation Principle (ISP)

Interfaces específicas y cohesivas:

- `IDataRepository`: Solo métodos para obtener datos
- `ISQLiteBuilder`: Solo métodos para construir SQLite
- No hay interfaces "gordas" con métodos innecesarios

### 5. Dependency Inversion Principle (DIP)

Dependencias hacia abstracciones:

```python
# ❌ Mal (acoplamiento directo)
class ExportService:
    def __init__(self):
        self.repo = PostgresRepository()  # Dependencia concreta

# ✅ Bien (inversión de dependencias)
class ExportService:
    def __init__(self, data_repository: IDataRepository):  # Dependencia de abstracción
        self.data_repository = data_repository
```

## Patrón DRY (Don't Repeat Yourself)

### Configuración Centralizada

```python
# Todas las configuraciones en un solo lugar
settings = get_settings()
```

### Logging Centralizado

```python
# Setup único de logger reutilizado en toda la app
logger = setup_logger(__name__)
```

### Excepciones Personalizadas

```python
# Jerarquía de excepciones reutilizables
ExportError
├── DatabaseConnectionError
├── DataFetchError
├── SQLiteCreationError
└── ValidationError
```

### Utilidades Compartidas

- `logger.py`: Configuración de logging
- `exceptions.py`: Excepciones personalizadas
- `settings.py`: Gestión de configuración

## Inyección de Dependencias

```python
# En handler.py
postgres_repo = PostgresRepository(...)  # Crear dependencias
sqlite_builder = SQLiteBuilder()

export_service = ExportService(         # Inyectar dependencias
    data_repository=postgres_repo,
    sqlite_builder=sqlite_builder
)
```

Beneficios:
- Facilita testing con mocks
- Desacoplamiento de componentes
- Configuración flexible
- Facilita cambios de implementación

## Testing Strategy

### Tests Unitarios

Pruebas aisladas de cada componente usando mocks:

```python
def test_export_service(mock_repository, mock_builder):
    service = ExportService(mock_repository, mock_builder)
    # Test aislado sin dependencias externas
```

### Tests de Integración

Pruebas con componentes reales:

```python
def test_postgres_repository_real_db():
    repo = PostgresRepository(...)
    # Test con base de datos real
```

## Extensibilidad

### Agregar Nueva Fuente de Datos

```python
class MySQLRepository(IDataRepository):
    def get_clientes_by_tenant(self, tenant_id: int):
        # Implementación para MySQL
        pass
```

### Agregar Nuevo Formato de Exportación

```python
class ICSVExporter(ABC):
    @abstractmethod
    def export_to_csv(self, data):
        pass

class CSVExporter(ICSVExporter):
    def export_to_csv(self, data):
        # Implementación CSV
        pass
```

## Manejo de Errores

Jerarquía de errores específicos del dominio:

```
Exception
└── ExportError
    ├── DatabaseConnectionError
    ├── DataFetchError
    ├── SQLiteCreationError
    └── ValidationError
```

Cada capa maneja sus propios errores y los propaga apropiadamente.

## Configuración por Entorno

```
.env.dev    → Desarrollo
.env.prod   → Producción
settings.py → Validación y gestión centralizada
```

Variables cargadas desde:
1. Variables de entorno de Lambda
2. Archivo .env (desarrollo local)
3. Valores por defecto en Settings

## Logging

Niveles de logging:
- **DEBUG**: Información detallada para desarrollo
- **INFO**: Información general de flujo
- **WARNING**: Advertencias
- **ERROR**: Errores que requieren atención

Formato estructurado para facilitar búsqueda en CloudWatch.
