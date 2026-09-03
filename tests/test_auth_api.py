"""Testes da feature 006 — Autenticação e API REST — quickstart C1-C4.

Test-First (constituição III). Usa client anônimo (sem login) p/ cenários de
auth e a API com token. O `client` do conftest é autenticado por padrão.
"""
import os

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.database import get_session
from app.main import app


@pytest.fixture()
def client_anon(db_engine):
    """Client sem login (para cenários de autenticação)."""

    def _override_get_session():
        with Session(db_engine) as session:
            yield session

    app.dependency_overrides[get_session] = _override_get_session
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def _senha():
    return os.environ.get("AUTOMATIC1_ADMIN_PASSWORD", "")


def _token():
    return os.environ.get("AUTOMATIC1_API_TOKEN", "")


# ---------------------------------------------------------------------------
# US1 — Autenticação web
# ---------------------------------------------------------------------------

def test_protecao_sem_sessao(client_anon):
    resp = client_anon.get("/setups", follow_redirects=False)
    assert resp.status_code == 302
    assert "/login" in resp.headers["location"]


def test_login_senha_incorreta(client_anon):
    resp = client_anon.post("/login", data={"senha": "errada"}, follow_redirects=False)
    assert resp.status_code == 200
    assert "incorreta" in resp.text.lower()
    assert "automatic1_session=" not in resp.headers.get("set-cookie", "")


def test_login_sucesso_concede_acesso(client_anon):
    resp = client_anon.post("/login", data={"senha": _senha(), "next": "/setups"}, follow_redirects=False)
    assert resp.status_code == 303
    assert "automatic1_session=" in resp.headers.get("set-cookie", "")

    pagina = client_anon.get("/setups", follow_redirects=False)
    assert pagina.status_code == 200


def test_logout_invalida_sessao(client_anon):
    client_anon.post("/login", data={"senha": _senha()})
    saida = client_anon.get("/logout", follow_redirects=False)
    assert saida.status_code == 303

    resp = client_anon.get("/setups", follow_redirects=False)
    assert resp.status_code == 302
    assert "/login" in resp.headers["location"]


def test_sem_configuracao_bloqueia(client_anon, monkeypatch):
    monkeypatch.delenv("AUTOMATIC1_ADMIN_PASSWORD", raising=False)
    monkeypatch.delenv("AUTOMATIC1_SESSION_SECRET", raising=False)

    pagina = client_anon.get("/login")
    assert pagina.status_code == 200
    assert "não configurada" in pagina.text.lower()

    post = client_anon.post("/login", data={"senha": "qualquer"}, follow_redirects=False)
    assert post.status_code == 200
    assert "não configurada" in post.text.lower()

    protegida = client_anon.get("/setups", follow_redirects=False)
    assert protegida.status_code == 302
    assert "/login" in protegida.headers["location"]


# ---------------------------------------------------------------------------
# US2 — API REST (somente leitura)
# ---------------------------------------------------------------------------

def test_api_sem_token(client_anon):
    resp = client_anon.get("/api/setups")
    assert resp.status_code == 401


def test_api_token_invalido(client_anon):
    resp = client_anon.get("/api/setups", headers={"Authorization": "Bearer errado"})
    assert resp.status_code == 401


def test_api_token_valido_lista_setups(client_anon, criar_setup):
    criar_setup(nome="API Setup", plataforma_alvo="Debian + Docker Swarm")
    resp = client_anon.get(
        "/api/setups",
        headers={"Authorization": f"Bearer {_token()}"},
    )
    assert resp.status_code == 200
    dados = resp.json()
    assert dados["total"] >= 1
    assert any(item["nome"] == "API Setup" for item in dados["itens"])


def test_api_maquinas_e_execucoes(client_anon, criar_setup, db_engine):
    from app.models import Execution, TargetHost

    with Session(db_engine) as session:
        host = TargetHost(nome="host-api", identificacao="203.0.113.50", created_by="admin", updated_by="admin")
        session.add(host)
        session.commit()
        session.refresh(host)
        setup = criar_setup(nome="Setup Exec API", plataforma_alvo="Debian + Docker Swarm")
        session.add(Execution(setup_id=setup.id, target_host_id=host.id, status="sucesso", created_by="admin"))
        session.commit()

    headers = {"Authorization": f"Bearer {_token()}"}
    maq = client_anon.get("/api/maquinas", headers=headers)
    assert maq.status_code == 200 and maq.json()["total"] >= 1

    execs = client_anon.get("/api/execucoes", headers=headers)
    assert execs.status_code == 200 and execs.json()["total"] >= 1
