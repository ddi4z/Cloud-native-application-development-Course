# Importamos la clase base y cada caso de uso 
from routes_app.domain.use_cases.base_use_case import BaseUseCase
from routes_app.domain.use_cases.create_trayecto_use_case import CreateTrayectoUseCase
from routes_app.domain.use_cases.get_trayecto_use_case import GetTrayectoUseCase
from routes_app.domain.use_cases.list_trayectos_use_case import ListTrayectosUseCase
from routes_app.domain.use_cases.delete_trayecto_use_case import DeleteTrayectoUseCase
from routes_app.domain.use_cases.get_trayecto_by_flight_id_use_case import GetTrayectoByFlightIdUseCase
from routes_app.domain.use_cases.count_trayectos_use_case import CountTrayectosUseCase
from routes_app.domain.use_cases.reset_trayectos_use_case import ResetTrayectosUseCase

# Importamos ports
from routes_app.domain.ports.routes_repository_port import RoutesRepositoryPort

# Importamos la implementación InMemory y Postgres 
from routes_app.adapters.memory.routes_repository_adapter import InMemoryRoutesRepositoryAdapter
from routes_app.adapters.postgres.routes_repository_adapter import PostgresRoutesRepositoryAdapter

# Instanciación del Repositorio

repository: RoutesRepositoryPort = InMemoryRoutesRepositoryAdapter()
# repository: RoutesRepositoryPort = PostgresRoutesRepositoryAdapter()


# Constructores (Builders) para cada caso de uso 

def build_create_trayecto_use_case() -> BaseUseCase:
    """Construye el caso de uso para crear un trayecto."""
    return CreateTrayectoUseCase(repository)

def build_get_trayecto_use_case() -> BaseUseCase:
    """Construye el caso de uso para obtener un trayecto por ID."""
    return GetTrayectoUseCase(repository)

def build_list_trayectos_use_case() -> BaseUseCase:
    """Construye el caso de uso para listar todos los trayectos."""
    return ListTrayectosUseCase(repository)

def build_delete_trayecto_use_case() -> BaseUseCase:
    """Construye el caso de uso para eliminar un trayecto."""
    return DeleteTrayectoUseCase(repository)

def build_get_trayecto_by_flight_id_use_case() -> BaseUseCase:
    """Construye el caso de uso para buscar un trayecto por flightId."""
    return GetTrayectoByFlightIdUseCase(repository)

def build_count_trayectos_use_case() -> BaseUseCase:
    """Construye el caso de uso para contar los trayectos."""
    return CountTrayectosUseCase(repository)

def build_reset_trayectos_use_case() -> BaseUseCase:
    """Construye el caso de uso para reiniciar el repositorio."""
    return ResetTrayectosUseCase(repository)