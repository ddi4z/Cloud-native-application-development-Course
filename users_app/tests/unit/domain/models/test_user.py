from datetime import datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from src.domain.models.user import User, UserStatus


def test_create_user_with_valid_data():
    valid_data = {
        "id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
        "username": "testuser",
        "email": "test@example.com",
        "phoneNumber": "+573001234567",
        "dni": "123456789",
        "fullName": "Test User",
        "password": "hashed_password_123",
        "salt": "random_salt",
        "token": "valid_auth_token",
        "status": UserStatus.VERIFIED,
        "expireAt": datetime.now(timezone.utc) + timedelta(hours=1),
        "createdAt": datetime.now(timezone.utc),
        "updatedAt": datetime.now(timezone.utc),
    }
    user = User(**valid_data)
    assert user.id == valid_data["id"]
    assert user.username == valid_data["username"]
    assert user.email == valid_data["email"]
    assert user.phoneNumber == valid_data["phoneNumber"]
    assert user.dni == valid_data["dni"]
    assert user.fullName == valid_data["fullName"]
    assert user.password == valid_data["password"]
    assert user.salt == valid_data["salt"]
    assert user.token == valid_data["token"]
    assert user.status == valid_data["status"]
    assert user.expireAt == valid_data["expireAt"]
    assert user.createdAt == valid_data["createdAt"]
    assert user.updatedAt == valid_data["updatedAt"]


def test_create_user_with_invalid_id():
    invalid_data = {
        "id": 1234,
        "username": "testuser",
        "email": "test@example.com",
        "password": "hashed_password_123",
        "salt": "random_salt",
        "token": "valid_auth_token",
        "status": UserStatus.VERIFIED,
        "expireAt": datetime.now(timezone.utc),
        "createdAt": datetime.now(timezone.utc),
        "updatedAt": datetime.now(timezone.utc),
    }
    with pytest.raises(ValidationError):
        User(**invalid_data)


def test_create_user_with_invalid_username_pattern():
    invalid_data = {
        "id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
        "username": "user with spaces",
        "email": "test@example.com",
        "password": "hashed_password_123",
        "salt": "random_salt",
        "token": "valid_auth_token",
        "status": UserStatus.VERIFIED,
        "expireAt": datetime.now(timezone.utc),
        "createdAt": datetime.now(timezone.utc),
        "updatedAt": datetime.now(timezone.utc),
    }
    with pytest.raises(ValidationError) as exc_info:
        User(**invalid_data)

    assert "username" in str(exc_info.value)
    assert "String should match pattern" in str(exc_info.value)


def test_create_user_with_empty_username():
    invalid_data = {
        "id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
        "username": "",  # Empty username
        "email": "test@example.com",
        "password": "hashed_password_123",
        "salt": "random_salt",
        "token": "valid_auth_token",
        "status": UserStatus.VERIFIED,
        "expireAt": datetime.now(timezone.utc),
        "createdAt": datetime.now(timezone.utc),
        "updatedAt": datetime.now(timezone.utc),
    }
    with pytest.raises(ValidationError) as exc_info:
        User(**invalid_data)

    assert "username" in str(exc_info.value)
    assert "String should have at least 1 character" in str(exc_info.value)


def test_create_user_with_invalid_email_format():
    invalid_data = {
        "id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
        "username": "testuser",
        "email": "invalid_email",  # Invalid email
        "password": "hashed_password_123",
        "salt": "random_salt",
        "token": "valid_auth_token",
        "status": UserStatus.VERIFIED,
        "expireAt": datetime.now(timezone.utc),
        "createdAt": datetime.now(timezone.utc),
        "updatedAt": datetime.now(timezone.utc),
    }
    with pytest.raises(ValidationError) as exc_info:
        User(**invalid_data)

    assert "email" in str(exc_info.value)
    assert "value is not a valid email address" in str(exc_info.value)


def test_create_user_with_missing_required_fields():
    with pytest.raises(ValidationError) as exc_info:
        User(
            id="a1b2c3d4-e5f6-7890-1234-567890abcdef",
            username="testuser",
            email="test@example.com",
        )
    error_message = str(exc_info.value)
    assert "password" in error_message
    assert "salt" in error_message
    assert "token" in error_message
    assert "status" in error_message
    assert "expireAt" in error_message
    assert "createdAt" in error_message
    assert "updatedAt" in error_message
