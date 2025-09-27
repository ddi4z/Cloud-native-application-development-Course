import hashlib
import time

import pytest

from src.adapters.postgres.user_repository_adapter import PostgresUserRepositoryAdapter
from src.domain.models.user import User, UserStatus
from src.domain.models.user_creation_request import UserCreationRequest
from src.domain.models.user_update_request import UserUpdateRequest
from src.errors import (
    InvalidCredentialsError,
    InvalidTokenError,
    MissingTokenError,
    MissingUserInformationError,
    UserAlreadyExistsError,
    UserNotFoundError,
)


def test_init_raises_error_if_no_db_url(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    with pytest.raises(ValueError, match="DATABASE_URL not set"):
        PostgresUserRepositoryAdapter()


def test_create_user_success(repo):
    creation_request = UserCreationRequest(
        username="new_user", email="new_user@example.com", password="secure_password"
    )
    user = repo.create(creation_request)

    assert isinstance(user, User)
    assert user.username == "new_user"
    assert user.email == "new_user@example.com"
    assert user.status == UserStatus.PENDING_VERIFICATION
    assert user.token is not None
    assert user.salt is not None
    assert user.password is not None


def test_create_user_already_exists_by_username(repo, create_user_db):
    create_user_db(
        username="existing_user",
        email="existing@example.com",
        password="p",
        salt="s",
        token="t",
    )

    creation_request = UserCreationRequest(
        username="existing_user", email="other@example.com", password="secure_password"
    )
    with pytest.raises(
        UserAlreadyExistsError, match="Username or email already exists."
    ):
        repo.create(creation_request)


def test_create_user_already_exists_by_email(repo, create_user_db):
    create_user_db(
        username="existing_user",
        email="existing@example.com",
        password="p",
        salt="s",
        token="t",
    )

    creation_request = UserCreationRequest(
        username="other_user", email="existing@example.com", password="secure_password"
    )
    with pytest.raises(
        UserAlreadyExistsError, match="Username or email already exists."
    ):
        repo.create(creation_request)


def test_create_user_with_missing_info(repo):
    creation_request = UserCreationRequest(
        username="new_user", email="new_user@example.com", password=""
    )
    with pytest.raises(
        MissingUserInformationError, match="Username, password, and email are required."
    ):
        repo.create(creation_request)


def test_update_user_success(repo, create_user_db):
    existing_user_db = create_user_db(
        username="old_user",
        email="old_user@example.com",
        password="p",
        salt="s",
        token="t",
    )
    user_id = existing_user_db.id
    initial_updated_at = existing_user_db.updatedAt

    update_request = UserUpdateRequest(
        fullName="Updated User Name", status=UserStatus.VERIFIED
    )

    time.sleep(0.01)

    updated_user = repo.update(user_id, update_request)

    assert updated_user.fullName == "Updated User Name"
    assert updated_user.status == UserStatus.VERIFIED
    assert updated_user.updatedAt > initial_updated_at


def test_update_user_not_found(repo):
    update_request = UserUpdateRequest(fullName="Nonexistent User")
    with pytest.raises(UserNotFoundError, match="User with id 999 not found."):
        repo.update(999, update_request)


def test_update_user_with_no_data(repo, create_user_db):
    existing_user_db = create_user_db(
        username="no_data_user",
        email="no_data_user@example.com",
        password="p",
        salt="s",
        token="t",
    )
    user_id = existing_user_db.id

    update_request = UserUpdateRequest()
    with pytest.raises(
        MissingUserInformationError,
        match="At least one field must be provided for update.",
    ):
        repo.update(user_id, update_request)


def test_authenticate_success(repo, create_user_db):
    password = "secure_password"
    salt = "random_salt"
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()

    create_user_db(
        username="auth_user",
        email="auth@example.com",
        password=password_hash,
        salt=salt,
        token="old_token",
    )

    authenticated_user = repo.authenticate("auth_user", password)

    assert authenticated_user is not None
    assert authenticated_user.username == "auth_user"
    assert authenticated_user.token != "old_token"


def test_authenticate_invalid_credentials_username(repo, create_user_db):
    password = "secure_password"
    salt = "random_salt"
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()

    create_user_db(
        username="valid_user",
        email="valid@example.com",
        password=password_hash,
        salt=salt,
        token="t",
    )

    with pytest.raises(InvalidCredentialsError, match="Invalid username or password."):
        repo.authenticate("invalid_username", password)


def test_authenticate_invalid_credentials_password(repo, create_user_db):
    password = "secure_password"
    salt = "random_salt"
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()

    create_user_db(
        username="valid_user",
        email="valid@example.com",
        password=password_hash,
        salt=salt,
        token="t",
    )

    with pytest.raises(InvalidCredentialsError, match="Invalid username or password."):
        repo.authenticate("valid_user", "wrong_password")


def test_authenticate_missing_info(repo):
    with pytest.raises(
        MissingUserInformationError, match="Username and password are required."
    ):
        repo.authenticate("", "password")


def test_get_current_user_missing_token(repo):
    with pytest.raises(
        MissingTokenError, match="Token is missing from the request header."
    ):
        repo.get_current_user(None)


def test_get_current_user_invalid_token(repo):
    with pytest.raises(InvalidTokenError, match="The token is invalid or has expired."):
        repo.get_current_user("invalid_token")


def test_count_users(repo, create_user_db):
    create_user_db(username="u1", email="e1@e.com", password="p", salt="s", token="t1")
    create_user_db(username="u2", email="e2@e.com", password="p", salt="s", token="t2")

    assert repo.count() == 2


def test_reset_users(repo, create_user_db):
    create_user_db(username="u1", email="e1@e.com", password="p", salt="s", token="t1")

    assert repo.count() == 1

    repo.reset()

    assert repo.count() == 0
