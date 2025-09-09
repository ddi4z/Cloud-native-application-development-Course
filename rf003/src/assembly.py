# from src.adapters.http import ADAPTER_HTTP

# from src.domain.ports.rf003_port import PORT

from src.domain.use_cases.base_use_case import BaseUseCase
from src.domain.use_cases.create_post import CreatePostUseCase


# Instanciar un puerto
repository = "DUMMY_STRING"

# ---- minimal clock ----
class SystemClock:
    def now(self):
        return datetime.now(timezone.utc)



def build_create_post_use_case() -> BaseUseCase:
    """Get create post use case."""
    return CreatePostUseCase(repository)

