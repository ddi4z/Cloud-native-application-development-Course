from src.domain.ports.rf003_port import UsersPort

class FakeUsers(UsersPort):
    def get_current_user(self, token: str) -> str:
        # accept any non-empty token for local dev
        return "user-123"