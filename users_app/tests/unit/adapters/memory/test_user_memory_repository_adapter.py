from datetime import datetime, timedelta
import os

import pytest

from src.domain.models.user import UserStatus
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

import hashlib
from src.domain.models.user_update_request import UserUpdateRequest
from src.domain.models.user_callback_request import UserCallbackRequest
from src.errors import UnauthorizedUserStatusError

def create_sample_user(
    memory_repo, username="testuser", email="test@example.com", password="password123"
):
    request = UserCreationRequest(
        username=username,
        email=email,
        password=password,
        phoneNumber="123456789",
        dni="100200300",
        fullName="Test User",
    )
    return memory_repo.create(request)


def test_create_user_success(memory_repo):
    user = create_sample_user(memory_repo)
    assert user.id in memory_repo.memory_store
    assert user.username == "testuser"
    assert user.status == UserStatus.PENDING_VERIFICATION
    assert memory_repo.count() == 1


def test_create_user_missing_information(memory_repo):
    request = UserCreationRequest(username="", email="email", password="pass")
    with pytest.raises(MissingUserInformationError):
        memory_repo.create(request)


def test_create_user_already_exists(memory_repo):
    create_sample_user(memory_repo)
    duplicate_request = UserCreationRequest(
        username="testuser", email="other@example.com", password="password123"
    )
    with pytest.raises(UserAlreadyExistsError):
        memory_repo.create(duplicate_request)


def test_update_user_not_found(memory_repo):
    with pytest.raises(UserNotFoundError):
        memory_repo.update("999", UserUpdateRequest(fullName="No User"))


def test_update_user_missing_data(memory_repo):
    user = create_sample_user(memory_repo)
    with pytest.raises(MissingUserInformationError):
        memory_repo.update(user.id, UserUpdateRequest())

def test_authenticate_invalid_credentials(memory_repo):
    create_sample_user(memory_repo, password="secret")
    with pytest.raises(InvalidCredentialsError):
        memory_repo.authenticate("testuser", "wrongpassword")


def test_authenticate_missing_information(memory_repo):
    with pytest.raises(MissingUserInformationError):
        memory_repo.authenticate("", "password")


def test_get_current_user_missing_token(memory_repo):
    with pytest.raises(MissingTokenError):
        memory_repo.get_current_user(None)


def test_get_current_user_invalid_token(memory_repo):
    with pytest.raises(InvalidTokenError):
        memory_repo.get_current_user("invalid-token")


def test_get_current_user_expired_token(memory_repo):
    user = create_sample_user(memory_repo)
    expired_time = (datetime.now() - timedelta(hours=2)).isoformat(timespec="seconds")
    user.expireAt = expired_time

    with pytest.raises(InvalidTokenError):
        memory_repo.get_current_user(user.token)




def test_authenticate_success(memory_repo):
    user = create_sample_user(memory_repo)
    memory_repo.update(user.id, UserUpdateRequest(status=UserStatus.VERIFIED))

    authenticated_user = memory_repo.authenticate("testuser", "password123")
    assert authenticated_user.id == user.id
    assert authenticated_user.token in memory_repo.tokens_store


def test_authenticate_user_not_verified(memory_repo):
    create_sample_user(memory_repo, password="password123")
    with pytest.raises(UnauthorizedUserStatusError):
        memory_repo.authenticate("testuser", "password123")


def test_get_current_user_success(memory_repo):
    user = create_sample_user(memory_repo)
    memory_repo.update(user.id, UserUpdateRequest(status=UserStatus.VERIFIED))
    user = memory_repo.authenticate("testuser", "password123")

    current = memory_repo.get_current_user(user.token)
    assert current.id == user.id
    assert current.username == "testuser"


def test_reset_clears_memory(memory_repo):
    create_sample_user(memory_repo)
    assert memory_repo.count() == 1
    memory_repo.reset()
    assert memory_repo.count() == 0
    assert memory_repo.tokens_store == {}


def test_patch_success(memory_repo):
    user = create_sample_user(memory_repo)
    os.environ["SECRET_TOKEN"] = "secret"  
    secret_token = os.getenv("SECRET_TOKEN")
    ruv = "RUV123"
    score = 90
    token_str = f"{secret_token}:{ruv}:{score}"
    verify_token = hashlib.sha256(token_str.encode()).hexdigest()

    callback = UserCallbackRequest(
        RUV=ruv,
        score=score,
        userIdentifier="uid",
        createdAt=datetime.now(),
        status="VERIFICADO",
        verifyToken=verify_token,
    )

    updated_user = memory_repo.patch(user.id, callback)
    assert updated_user.status == UserStatus.VERIFIED


def test_patch_invalid_token(memory_repo):
    user = create_sample_user(memory_repo)
    callback = UserCallbackRequest(
        RUV="bad",
        score=0,
        userIdentifier="uid",
        createdAt=datetime.now(),
        status="VERIFICADO",
        verifyToken="invalidhash",
    )
    with pytest.raises(AssertionError):
        memory_repo.patch(user.id, callback)
