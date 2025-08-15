
from src.domain.use_cases.base_use_case import BaseUseCase
from src.domain.use_cases.create_user_use_case import CreateUserUseCase
from src.domain.use_cases.update_user_use_case import UpdateUserUseCase
from src.domain.use_cases.authenticate_user_use_case import AuthenticateUserUseCase
from src.domain.use_cases.get_current_user_use_case import GetCurrentUserUseCase
from src.domain.use_cases.get_users_count_use_case import GetUsersCountUseCase
from src.domain.use_cases.reset_users_use_case import ResetUsersUseCase
from src.domain.ports.user_repository_port import UserRepositoryPort

from src.adapters.postgres.user_repository_adapter import PostgresUserRepositoryAdapter
from src.adapters.memory.user_repository_adapter import InMemoryUserRepositoryAdapter

# Shared in-memory repository instance for all user use cases
#repository: UserRepositoryPort = InMemoryUserRepositoryAdapter()
repository: UserRepositoryPort = PostgresUserRepositoryAdapter()


def build_create_user_use_case() -> BaseUseCase:
    """Get create user use case."""
    return CreateUserUseCase(repository)


def build_update_user_use_case() -> BaseUseCase:
    """Get update user use case."""
    return UpdateUserUseCase(repository)


def build_authenticate_user_use_case() -> BaseUseCase:
    """Get authenticate user use case."""
    return AuthenticateUserUseCase(repository)


def build_get_current_user_use_case() -> BaseUseCase:
    """Get current user use case."""
    return GetCurrentUserUseCase(repository)


def build_get_users_count_use_case() -> BaseUseCase:
    """Get users count use case."""
    return GetUsersCountUseCase(repository)


def build_reset_users_use_case() -> BaseUseCase:
    """Get reset users use case."""
    return ResetUsersUseCase(repository)
