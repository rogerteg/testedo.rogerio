"""Configurações centrais da aplicação (lidas de variáveis de ambiente)."""
import os
from functools import lru_cache
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings:
    """Configurações do Automatic1 Admin."""

    def __init__(self) -> None:
        self.db_path: Path = Path(os.getenv("DB_PATH", str(BASE_DIR / "data" / "setups.db")))
        self.operator_name: str = os.getenv("OPERATOR_NAME", "admin")
        self.app_version: str = os.getenv("APP_VERSION", "0.1.0")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
