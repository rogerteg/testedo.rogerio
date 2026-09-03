"""Engine/sessão SQLite e inicialização idempotente do schema."""
from sqlmodel import Session, SQLModel, create_engine

from .config import settings

# Garante que o diretório do banco exista (data/)
settings.db_path.parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(
    f"sqlite:///{settings.db_path}",
    connect_args={"check_same_thread": False},
)


def init_db() -> None:
    """Cria o schema de forma idempotente (FR-012: persistência durável)."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Dependência do FastAPI que fornece uma Sessão de banco."""
    with Session(engine) as session:
        yield session
