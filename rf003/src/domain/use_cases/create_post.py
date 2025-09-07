from datetime import datetime, timezone
import hashlib

from src.domain.models.publication_request import PublicationRequest
from src.domain.models.publication_result import PublicationResult
from src.domain.models.auth_context import AuthContext
from src.domain.ports.rf003_port import UsersPort, RoutesPort, PostsPort, UniquesPort, Clock
from src.errors import UnauthorizedError, ValidationError, ConflictError, DependencyError

def _route_fp(r) -> str:
    key = f"{r.origin.strip().lower()}|{r.destination.strip().lower()}|{r.departure_at.astimezone(timezone.utc).isoformat()}"
    return hashlib.sha256(key.encode()).hexdigest()

class CreatePublicationUseCase:
    def __init__(
        self,
        users: UsersPort,
        routes: RoutesPort,
        posts: PostsPort,
        uniques: UniquesPort,
        clock: Clock,
    ):
        self.users = users
        self.routes = routes
        self.posts = posts
        self.uniques = uniques
        self.clock = clock

    def execute(self, auth: AuthContext, req: PublicationRequest) -> PublicationResult:
        if not auth or not auth.token:
            raise UnauthorizedError("Missing token")
        user_id = self.users.get_current_user(auth.token)

        now = self.clock.now() if hasattr(self.clock, "now") else datetime.now(timezone.utc)

        # RF003 date rules
        if not (req.route.departure_at > now):
            raise ValidationError("departure_at must be in the future")
        if not (req.post.expires_at > now and req.post.expires_at <= req.route.departure_at):
            raise ValidationError("expires_at must be > now and <= departure_at")

        fp = _route_fp(req.route)

        # uniqueness guard (user + route)
        if not self.uniques.try_claim(user_id, fp):
            raise ConflictError("User already has a publication for this route")

        try:
            route_id = self.routes.find_by_fingerprint(fp)
            if not route_id:
                route_id = self.routes.create(req.route)

            if self.posts.user_has_post_for_route(user_id, route_id):
                raise ConflictError("User already has a publication for this route")

            post_id = self.posts.create(user_id, route_id, req)

            return PublicationResult(
                post_id=post_id,
                route_id=route_id,
                user_id=user_id,
                created_at=now,
            )
        except ConflictError:
            # keep the claim to block duplicates
            raise
        except Exception as e:
            # release claim so user can retry
            self.uniques.release(user_id, fp)
            raise DependencyError(str(e)) from e