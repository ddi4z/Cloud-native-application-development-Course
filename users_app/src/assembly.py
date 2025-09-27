import os

from src.adapters.memory.user_repository_adapter import InMemoryUserRepositoryAdapter
from src.adapters.postgres.user_repository_adapter import PostgresUserRepositoryAdapter
from src.adapters.sqs.sqs_email_adapter import SQSMessageQueueAdapter
from src.adapters.true_native_identity_verifier_adapter import (
    TrueNativeIdentityVerifierAdapter,
)
from src.domain.ports.identity_verifier_port import IdentityVerifierPort
from src.domain.ports.message_queue_port import MessageQueuePort
from src.domain.ports.user_repository_port import UserRepositoryPort
from src.domain.use_cases.authenticate_user_use_case import AuthenticateUserUseCase
from src.domain.use_cases.base_use_case import BaseUseCase
from src.domain.use_cases.create_user_use_case import CreateUserUseCase
from src.domain.use_cases.create_user_with_verification_use_case import (
    CreateUserWithVerificationUseCase,
)
from src.domain.use_cases.get_current_user_use_case import GetCurrentUserUseCase
from src.domain.use_cases.get_users_count_use_case import GetUsersCountUseCase
from src.domain.use_cases.identity_verifier_use_case import (
    IdentityVerifierUseCase,
)
from src.domain.use_cases.patch_user_use_case import PatchUserUseCase
from src.domain.use_cases.reset_users_use_case import ResetUsersUseCase
from src.domain.use_cases.send_user_email_use_case import SendUserEmailUseCase
from src.domain.use_cases.update_user_status_use_case import UpdateUserStatusUseCase
from src.domain.use_cases.update_user_use_case import UpdateUserUseCase

# Shared in-memory repository instance for all user use cases
# repository: UserRepositoryPort = InMemoryUserRepositoryAdapter()

identity_verifier_url = os.getenv("IDENTITY_VERIFIER_SERVICE_URL")
if not identity_verifier_url:
    raise EnvironmentError("IDENTITY_VERIFIER_SERVICE_URL environment variable not set")

user_repository: UserRepositoryPort = PostgresUserRepositoryAdapter()

queue_adapter: MessageQueuePort = SQSMessageQueueAdapter()

identity_verifier_adapter: IdentityVerifierPort = TrueNativeIdentityVerifierAdapter(
    identity_verifier_url
)


def build_create_user_use_case() -> BaseUseCase:
    """Get create user use case."""
    return CreateUserUseCase(user_repository)


def build_update_user_use_case() -> BaseUseCase:
    """Get update user use case."""
    return UpdateUserUseCase(user_repository)


def build_update_user_use_case() -> BaseUseCase:
    """Get update user use case."""
    return UpdateUserUseCase(user_repository)


def build_patch_user_use_case() -> BaseUseCase:
    """Get patch user use case."""
    return PatchUserUseCase(user_repository)


def build_authenticate_user_use_case() -> BaseUseCase:
    """Get authenticate user use case."""
    return AuthenticateUserUseCase(user_repository)


def build_get_current_user_use_case() -> BaseUseCase:
    """Get current user use case."""
    return GetCurrentUserUseCase(user_repository)


def build_get_users_count_use_case() -> BaseUseCase:
    """Get users count use case."""
    return GetUsersCountUseCase(user_repository)


def build_reset_users_use_case() -> BaseUseCase:
    """Get reset users use case."""
    return ResetUsersUseCase(user_repository)


def build_send_user_email_message_use_case() -> BaseUseCase:
    """Get send user email message use case."""
    return SendUserEmailUseCase(queue_adapter)


def build_update_user_status_use_case() -> BaseUseCase:
    """Get update user status use case."""
    patch_use_case = build_patch_user_use_case()
    email_use_case = build_send_user_email_message_use_case()
    return UpdateUserStatusUseCase(patch_use_case, email_use_case)


def build_identity_verifier_use_case() -> BaseUseCase:
    """Get identity verifier use case."""
    return IdentityVerifierUseCase(identity_verifier=identity_verifier_adapter)


def build_create_user_with_verification_use_case() -> BaseUseCase:
    """Get create user with verification use case."""
    create_user_uc = build_create_user_use_case()
    verify_identity_uc = build_identity_verifier_use_case()
    return CreateUserWithVerificationUseCase(create_user_uc, verify_identity_uc)
