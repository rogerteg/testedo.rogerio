"""Modelo de persistência do catálogo de setups (ver data-model.md)."""
from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


def _utcnow() -> datetime:
    return datetime.now(UTC)


class EnvironmentSetup(SQLModel, table=True):
    """Registro de um ambiente/setup que o Automatic1 pode provisionar."""

    __tablename__ = "environment_setup"

    id: int | None = Field(default=None, primary_key=True)
    nome: str = Field(index=True, max_length=120)
    descricao: str | None = Field(default=None, max_length=2000)
    plataforma_alvo: str = Field(max_length=60)
    origem_asset: str = Field(max_length=500)
    versao: str | None = Field(default=None, max_length=64)
    hash: str | None = Field(default=None, max_length=256)
    licenca: str | None = Field(default=None, max_length=500)
    status: str = Field(default="rascunho", index=True, max_length=32)
    categoria: str | None = Field(default=None, index=True, max_length=32)
    resultado_ultima_execucao: str | None = Field(default=None, max_length=1000)
    created_at: datetime = Field(default_factory=_utcnow)
    updated_at: datetime = Field(default_factory=_utcnow)
    created_by: str | None = Field(default=None, max_length=120)
    updated_by: str | None = Field(default=None, max_length=120)
