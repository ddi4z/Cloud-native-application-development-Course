from datetime import datetime, timedelta, timezone
from uuid import UUID

import pytest
from pydantic import ValidationError

from src.domain.models.posts import Post


def test_create_post_with_valid_data():
    valid_data = {
        "id": "33333333-3333-3333-3333-333333333333",
        "routeId": "11111111-1111-1111-1111-111111111111",
        "userId": "22222222-2222-2222-2222-222222222222",
        "expireAt": datetime.now(timezone.utc) + timedelta(hours=24),
        "createdAt": datetime.now(timezone.utc),
    }
    post = Post(**valid_data)

    assert post.id == UUID(valid_data["id"])
    assert post.routeId == UUID(valid_data["routeId"])
    assert post.userId == UUID(valid_data["userId"])

    assert isinstance(post.expireAt, datetime)
    assert isinstance(post.createdAt, datetime)

    assert post.expireAt.tzinfo is not None
    assert post.createdAt.tzinfo is not None
