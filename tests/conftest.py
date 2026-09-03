"""Fixtures de teste: SQLite em memória isolado por teste + TestClient.

A app usa SQLite em arquivo (config default); nos testes sobrescrevemos a
dependência de sessão para um banco em memória (StaticPool), garantindo
isolamento por teste e nenhum efeito colateral em data/setups.db.
"""
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.database import get_session
from app.main import app
from app.models import EnvironmentSetup


@pytest.fixture()
def db_engine():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture()
def client(db_engine):
    def _override_get_session():
        with Session(db_engine) as session:
            yield session

    app.dependency_overrides[get_session] = _override_get_session
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def criar_setup(db_engine):
    """Helper que persiste um EnvironmentSetup direto no banco de teste."""

    def _criar(**campos):
        dados = {
            "nome": "Setup Padrão",
            "plataforma_alvo": "Windows",
            "origem_asset": "https://github.com/exemplo/setup",
            "status": "ativo",
        }
        dados.update(campos)
        dados.setdefault("updated_at", datetime.now(timezone.utc))
        with Session(db_engine) as session:
            obj = EnvironmentSetup(**dados)
            session.add(obj)
            session.commit()
            session.refresh(obj)
            return obj

    return _criar
