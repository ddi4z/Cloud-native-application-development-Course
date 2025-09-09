from sqlalchemy import create_engine, text
from src.domain.ports.rf003_port import UniquesPort

class SqliteUniques(UniquesPort):
    def __init__(self, url="sqlite:///./uniques.db"):
        self.engine = create_engine(url, future=True)
        with self.engine.begin() as cx:
            cx.execute(text("""
                CREATE TABLE IF NOT EXISTS user_route_uniques(
                  user_id TEXT NOT NULL,
                  route_fp TEXT NOT NULL,
                  PRIMARY KEY (user_id, route_fp)
                );
            """))
    def try_claim(self, user_id: str, route_fp: str) -> bool:
        try:
            with self.engine.begin() as cx:
                cx.execute(
                    text("INSERT INTO user_route_uniques(user_id, route_fp) VALUES (:u, :r)"),
                    {"u": user_id, "r": route_fp}
                )
            return True
        except Exception:
            return False

    def release(self, user_id: str, route_fp: str) -> None:
        with self.engine.begin() as cx:
            cx.execute(
                text("DELETE FROM user_route_uniques WHERE user_id=:u AND route_fp=:r"),
                {"u": user_id, "r": route_fp}
            )