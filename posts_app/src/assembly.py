from posts_app.src.adapters.postgres.post_repository_adapter import (
    PostgresPostRepositoryAdapter,
)
from src.domain.ports.post_repository_port import PostRepositoryPort
from src.domain.use_cases.base_use_case import BaseUseCase
from src.domain.use_cases.count_post_use_case import CountPostUseCase
from src.domain.use_cases.create_post_use_case import CreatePostUseCase
from src.domain.use_cases.delete_post_use_case import DeletePostUseCase
from src.domain.use_cases.filter_post_use_case import FilterPostUseCase
from src.domain.use_cases.query_post_use_case import QueryPostUseCase
from src.domain.use_cases.reset_post_use_case import ResetPostUseCase

# from src.adapters.memory.post_repository_adapter import InMemoryPostRepositoryAdapter

# Shared in-memory repository instance for all post use cases
# repository: PostRepositoryPort = InMemoryPostRepositoryAdapter()
repository: PostRepositoryPort = PostgresPostRepositoryAdapter()


def build_create_post_use_case() -> BaseUseCase:
    """Get create post use case."""
    return CreatePostUseCase(repository)


def build_count_post_use_case() -> BaseUseCase:
    """Get count post use case."""
    return CountPostUseCase(repository)


def build_delete_post_use_case() -> BaseUseCase:
    """Get delete post use case."""
    return DeletePostUseCase(repository)


def build_filter_post_use_case() -> BaseUseCase:
    """Get filter post use case."""
    return FilterPostUseCase(repository)


def build_query_post_use_case() -> BaseUseCase:
    """Get post query use case."""
    return QueryPostUseCase(repository)


def build_reset_post_use_case() -> BaseUseCase:
    """Get reset post use case."""
    return ResetPostUseCase(repository)
