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
    # Feature 009 — config de deploy por setup (sem segredos; const. IV).
    dominio: str | None = Field(default=None, max_length=255)
    variaveis_deploy: str | None = Field(default=None, max_length=4000)
    status: str = Field(default="rascunho", index=True, max_length=32)
    categoria: str | None = Field(default=None, index=True, max_length=32)
    resultado_ultima_execucao: str | None = Field(default=None, max_length=1000)
    created_at: datetime = Field(default_factory=_utcnow)
    updated_at: datetime = Field(default_factory=_utcnow)
    created_by: str | None = Field(default=None, max_length=120)
    updated_by: str | None = Field(default=None, max_length=120)


# Plataforma/ambiente-alvo padrão (features 002/003 — valor controlado).
PLATAFORMA_PADRAO = "Debian + Docker Swarm"


class TargetHost(SQLModel, table=True):
    """Máquina alvo onde o Automatic1 pode provisionar setups (feature 003).

    Apenas metadados — **nenhuma credencial** (constituição IV / FR-004).
    """

    __tablename__ = "target_host"

    id: int | None = Field(default=None, primary_key=True)
    nome: str = Field(index=True, max_length=120)
    identificacao: str = Field(max_length=255)
    plataforma_alvo: str = Field(default=PLATAFORMA_PADRAO, max_length=60)
    descricao: str | None = Field(default=None, max_length=1000)
    status: str = Field(default="ativa", index=True, max_length=32)
    created_at: datetime = Field(default_factory=_utcnow)
    updated_at: datetime = Field(default_factory=_utcnow)
    created_by: str | None = Field(default=None, max_length=120)
    updated_by: str | None = Field(default=None, max_length=120)


class Execution(SQLModel, table=True):
    """Registro (imutável) de execução de um setup numa máquina — feature 003.

    Nesta etapa é **registro/estado**: nenhuma execução real é disparada
    (provisionamento real = Etapa 3 / feature 004).
    """

    __tablename__ = "execution"

    id: int | None = Field(default=None, primary_key=True)
    setup_id: int = Field(foreign_key="environment_setup.id", index=True)
    target_host_id: int = Field(foreign_key="target_host.id", index=True)
    status: str = Field(index=True, max_length=32)
    resumo: str | None = Field(default=None, max_length=1000)
    log: str | None = Field(default=None)
    exit_code: int | None = Field(default=None)
    started_at: datetime | None = Field(default=None)
    finished_at: datetime | None = Field(default=None)
    created_at: datetime = Field(default_factory=_utcnow)
    created_by: str | None = Field(default=None, max_length=120)


class Agendamento(SQLModel, table=True):
    """Agendamento cron de provisionamento de um setup numa máquina (feature 012).

    Expressão de 5 campos (`minuto hora dia mês dia-semana`), parser caseiro.
    Disparo recorrente reusa as guardas (004) e o worker assíncrono (008).
    """

    __tablename__ = "agendamento"

    id: int | None = Field(default=None, primary_key=True)
    setup_id: int = Field(foreign_key="environment_setup.id", index=True)
    target_host_id: int = Field(foreign_key="target_host.id", index=True)
    cron: str = Field(default="0 * * * *", max_length=100)
    ativo: bool = Field(default=True, index=True)
    ultimo_disparo: datetime | None = Field(default=None)
    created_at: datetime = Field(default_factory=_utcnow)
    updated_at: datetime = Field(default_factory=_utcnow)
    created_by: str | None = Field(default=None, max_length=120)
    updated_by: str | None = Field(default=None, max_length=120)
