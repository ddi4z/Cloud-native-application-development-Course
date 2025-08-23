import pytest
from datetime import datetime, timedelta, timezone
from pydantic import ValidationError
from src.domain.models.posts import Post


from uuid import UUID
from datetime import datetime, timedelta, timezone
from src.domain.models.post_db import PostDB



def test_create_post_with_valid_data():
    valid_data = {
        'id':'33333333-3333-3333-3333-333333333333',
        'routeId':"11111111-1111-1111-1111-111111111111",
        'userId':"22222222-2222-2222-2222-222222222222",
        'expireAt':datetime.now(timezone.utc) + timedelta(hours=24),
        'createdAt':datetime.now(timezone.utc)
    }
    post = Post(**valid_data)

    assert post.id == valid_data["id"]   
    assert post.routeId == valid_data["routeId"]   
    assert post.userId == valid_data["userId"]
    assert post.expireAt == valid_data["expireAt"]
    assert post.createdAt == valid_data["createdAt"]

def test_create_post_with_invalid_id():
    invalid_data = {
        'id':12345,
        'routeId':"11111111-1111-1111-1111-111111111111",
        'userId':"22222222-2222-2222-2222-222222222222",
        'expireAt':datetime.now(timezone.utc) + timedelta(hours=24),
        'createdAt':datetime.now(timezone.utc)
    }
    with pytest.raises(ValidationError):
        Post(**invalid_data)


def test_create_post_with_invalid_route_pattern():
    invalid_data = {
        'id':'33333333-3333-3333-3333-333333333333',
        'routeId':1111,
        'userId':"22222222-2222-2222-2222-222222222222",
        'expireAt':datetime.now(timezone.utc) + timedelta(hours=24),
        'createdAt':datetime.now(timezone.utc)
    }
    with pytest.raises(ValidationError) as exc_info:
        Post(**invalid_data)


def test_create_post_with_invalid_user_pattern():
    invalid_data = {
        'id':'33333333-3333-3333-3333-333333333333',
        'routeId':"11111111-1111-1111-1111-111111111111",
        'userId':1111,
        'expireAt':datetime.now(timezone.utc) + timedelta(hours=24),
        'createdAt':datetime.now(timezone.utc)
    }
    with pytest.raises(ValidationError) as exc_info:
        Post(**invalid_data)

def test_create_post_with_invalid_expireat_pattern():
    invalid_data = {
        'id':'33333333-3333-3333-3333-333333333333',
        'routeId':"11111111-1111-1111-1111-111111111111",
        'userId':"22222222-2222-2222-2222-222222222222",
        'expireAt':12345,
        'createdAt':datetime.now(timezone.utc)
    }
    with pytest.raises(ValidationError) as exc_info:
        Post(**invalid_data)

def test_create_post_with_invalid_createdat_pattern():
    invalid_data = {
        'id':'33333333-3333-3333-3333-333333333333',
        'routeId':"11111111-1111-1111-1111-111111111111",
        'userId':"22222222-2222-2222-2222-222222222222",
        'expireAt':datetime.now(timezone.utc) + timedelta(hours=24),
        'createdAt':12354
    }
    with pytest.raises(ValidationError) as exc_info:
        Post(**invalid_data)


def test_create_post_with_missing_required_fields():
    with pytest.raises(ValidationError) as exc_info:
        Post(
            id="33333333-3333-3333-3333-333333333333",
            routeId='33333333-3333-3333-3333-333333333333'
        )