from datetime import datetime, timedelta, timezone
from src.domain.models.user_db import UserDB
from src.domain.models.user import UserStatus

def test_create_user_db_with_valid_data(db_session):
    user_data = UserDB(
        username="testuser",
        email="test@example.com",
        phoneNumber="+573001234567",
        dni="123456789",
        fullName="Test User",
        password="hashed_password",
        salt="random_salt",
        token="valid_token",
        status=UserStatus.VERIFIED,
        expireAt=datetime.now(timezone.utc) + timedelta(hours=1),
    )
    db_session.add(user_data)
    db_session.commit()
    retrieved_user = db_session.query(UserDB).filter_by(username="testuser").first()
    assert retrieved_user is not None
    assert retrieved_user.username == "testuser"
    assert retrieved_user.email == "test@example.com"
    assert retrieved_user.phoneNumber == "+573001234567"
    assert retrieved_user.dni == "123456789"
    assert retrieved_user.fullName == "Test User"
    assert retrieved_user.password == "hashed_password"
    assert retrieved_user.salt == "random_salt"
    assert retrieved_user.token == "valid_token"
    assert retrieved_user.status == UserStatus.VERIFIED
    assert isinstance(retrieved_user.id, str)
    assert retrieved_user.createdAt is not None
    assert retrieved_user.updatedAt is not None

def test_default_values(db_session):
    user = UserDB(
        username="default_user",
        email="default@example.com",
        password="hashed_password",
        salt="random_salt",
        token="valid_token",
        status=UserStatus.PENDING_VERIFICATION,
        expireAt=datetime.now(timezone.utc) + timedelta(hours=1),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    assert isinstance(user.id, str)
    assert user.createdAt is not None
    assert user.updatedAt is not None
    assert user.createdAt == user.updatedAt

