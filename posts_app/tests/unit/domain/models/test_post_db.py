from uuid import UUID
from datetime import datetime, timedelta, timezone
from src.domain.models.post_db import PostDB

def test_create_post_db_with_valid_data(db_session):
    post_data = PostDB(
        id=UUID('33333333-3333-3333-3333-333333333333'),
        routeId=UUID("11111111-1111-1111-1111-111111111111"),
        userId=UUID("22222222-2222-2222-2222-222222222222"),
        expireAt=datetime.now(timezone.utc) + timedelta(hours=24),
        createdAt=datetime.now(timezone.utc)
        
        )
    
    db_session.add(post_data)
    db_session.commit()
    retrieved_post = db_session.query(PostDB).filter_by(id=UUID('33333333-3333-3333-3333-333333333333')).first()

    assert retrieved_post is not None
    assert retrieved_post.id == UUID('33333333-3333-3333-3333-333333333333')
    assert retrieved_post.routeId == UUID("11111111-1111-1111-1111-111111111111")
    assert retrieved_post.expireAt is not None
    assert retrieved_post.createdAt is not None
    assert isinstance(retrieved_post.id, UUID)