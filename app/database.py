"""Engine/sessão SQLite e inicialização idempotente do schema."""
from sqlalchemy import text
from sqlmodel import Session, SQLModel, create_engine

from .config import settings

# Garante que o diretório do banco exista (data/)
settings.db_path.parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(
    f"sqlite:///{settings.db_path}",
    connect_args={"check_same_thread": False},
)


def _migrar_schema() -> None:
    """Migrações aditivas idempotentes (feature 002, research D5).

    `create_all` não adiciona colunas em tabelas existentes; bancos criados
    pela feature `001` precisam da coluna ``categoria`` adicionada via ALTER.
    """
    with engine.begin() as conn:
        colunas = [linha[1] for linha in conn.execute(text("PRAGMA table_info(environment_setup)"))]
        if "categoria" not in colunas:
            conn.execute(
                text("ALTER TABLE environment_setup ADD COLUMN categoria VARCHAR(32)")
            )


def init_db() -> None:
    """Cria o schema de forma idempotente (FR-012: persistência durável)."""
    SQLModel.metadata.create_all(engine)
    _migrar_schema()


def get_session():
    """Dependência do FastAPI que fornece uma Sessão de banco."""
    with Session(engine) as session:
        yield session
