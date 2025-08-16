import os
from typing import Dict, Optional, List
from uuid import uuid4, UUID
from datetime import datetime, timedelta, timezone
import hashlib

from src.domain.models.posts import Post
from src.domain.ports.post_repository_port import PostRepositoryPort
from src.errors import InvalidCredentialsError, MissingIdError, MissingPostInformationError, InvalidExpirationDate, PostNotFoundError

from src.domain.models.post_creation_request import PostCreationRequest


class InMemoryUserRepositoryAdapter(PostRepositoryPort):
    """In-memory implementation of UserRepository."""

    memory_store: Dict[UUID, Post] = {}

    def sequence(self) -> int:
        """Generate a new unique ID."""
        return uuid4()


    def create(self, post_dto: PostCreationRequest) -> Post:
        """Create a new post."""

        if not all([post_dto.routeId, post_dto.expireAt, post_dto.userId]):
            raise MissingPostInformationError("Route Id, Expiration date, and User id are all required.")
        
        if post_dto.expireAt <= datetime.now(timezone.utc):
            raise InvalidExpirationDate("Expiration date must be in the future.")

        time_now = datetime.now().isoformat(timespec="seconds")

        post = Post(
            id=self.sequence,
            routeId=post_dto.routeId,
            userId=post_dto.userId,
            expireAt=post_dto.expireAt,
            createdAt=time_now
            )

        self.memory_store[post.id] = post

        return post
    


    def filter(self, 
               expire: Optional[bool]= None,
               route: Optional[UUID] = None,
               owner: Optional[UUID] = None,
    ) -> List[Post]:
        
        """Get a list of post matching certain criteria """
        items: List[Post] = list(self.memory_store.values())
        now = datetime.now().isoformat(timespec="seconds")

        def is_expired(p: Post) -> bool:
            return p.expireAt is not None and p.expireAt <= now

        if expire is not None:
            items = [p for p in items if (is_expired(p) if expire else not is_expired(p))]

        if route is not None:
            items = [p for p in items if getattr(p, "routeId", None) == route]

        if owner is not None:
            items = [p for p in items if getattr(p, "userId", None) == owner]
            
        return items



    def query(self, id: UUID) -> Optional[Post]:
        """Get information on a specific post"""
        if not id:
            raise MissingIdError("Id is missing from the request header.")
        
        post = self.memory_store.get(id)

        if not post:
            raise PostNotFoundError("The provided id is not in the database")
        return post



    def delete(self, id: UUID) -> None:
        """Delete a post by id."""

        # Not missing id
        if id is None or (isinstance(id, str) and not id.strip()):
            raise MissingIdError("Id is missing from the request header.")

        # Parse/validar UUID
        if isinstance(id, UUID):
            post_id = id
        else:
            try:
                post_id = UUID(id)
            except Exception:
                raise InvalidCredentialsError("Id must be a string with UUID format.")

        # No encontrado
        try:
            post_del = self.memory_store[post_id]
            del self.memory_store[post_id]
            return post_del
        except KeyError:
            raise PostNotFoundError("The provided id is not in the database")



    def count(self) -> int:
        """Get total number of users."""
        return len(self.memory_store)


    def reset(self) -> None:
        """Delete all users."""
        self.memory_store.clear()

