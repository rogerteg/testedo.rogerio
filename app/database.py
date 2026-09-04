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
    """Migrações aditivas idempotentes (features 002/004, research).

    `create_all` não adiciona colunas em tabelas existentes; colunas novas são
    adicionadas via ALTER quando ausentes (PRAGMA table_info).
    """
    with engine.begin() as conn:
        def _garantir_colunas(tabela: str, adicoes: dict[str, str]) -> None:
            colunas = {linha[1] for linha in conn.execute(text(f"PRAGMA table_info({tabela})"))}
            for nome, tipo in adicoes.items():
                if nome not in colunas:
                    conn.execute(text(f"ALTER TABLE {tabela} ADD COLUMN {nome} {tipo}"))

        _garantir_colunas("environment_setup", {"categoria": "VARCHAR(32)"})
        _garantir_colunas(
            "execution",
            {
                "log": "TEXT",
                "exit_code": "INTEGER",
                "started_at": "DATETIME",
                "finished_at": "DATETIME",
            },
        )
        _garantir_colunas(
            "environment_setup",
            {
                "dominio": "VARCHAR(255)",
                "variaveis_deploy": "TEXT",
            },
        )


def init_db() -> None:
    """Cria o schema de forma idempotente (FR-012: persistência durável)."""
    SQLModel.metadata.create_all(engine)
    _migrar_schema()


def get_session():
    """Dependência do FastAPI que fornece uma Sessão de banco."""
    with Session(engine) as session:
        yield session
