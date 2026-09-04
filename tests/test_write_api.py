"""Testes da feature 007 — API de Escrita — quickstart C1-C4.

Test-First (constituição III). Usa o token de escrita (conftest) e client.
"""
import os

from sqlmodel import Session

from app.models import TargetHost

TOKEN = "Bearer "


def _write_token():
    return os.environ.get("AUTOMATIC1_WRITE_API_TOKEN", "")


def _read_token():
    return os.environ.get("AUTOMATIC1_API_TOKEN", "")


def _wh():
    return {"Authorization": f"Bearer {_write_token()}"}


def _payload_setup(**campos):
    dados = {
        "nome": "Api Setup",
        "plataforma_alvo": "Debian + Docker Swarm",
        "origem_asset": "https://raw.githubusercontent.com/acme/setup/main/install.sh",
    }
    dados.update(campos)
    return dados


def _criar_maquina(client):
    return client.post(
        "/api/maquinas",
        json={"nome": "srv-api-01", "identificacao": "203.0.113.99"},
        headers=_wh(),
    )


# ---------------------------------------------------------------------------
# US1 — Criar setup/máquina via API
# ---------------------------------------------------------------------------

def test_criar_setup_201(client):
    resp = client.post("/api/setups", json=_payload_setup(), headers=_wh())
    assert resp.status_code == 201
    assert resp.json()["nome"] == "Api Setup"


def test_criar_setup_duplicado_409(client):
    client.post("/api/setups", json=_payload_setup(), headers=_wh())
    resp = client.post("/api/setups", json=_payload_setup(nome="api setup"), headers=_wh())
    assert resp.status_code == 409
    erros = resp.json()["detail"]["erros"]
    assert "nome" in erros


def test_criar_setup_campo_obrigatorio_422(client):
    resp = client.post("/api/setups", json={"nome": "Sem origem"}, headers=_wh())
    assert resp.status_code == 422
    erros = resp.json()["detail"]["erros"]
    assert "origem_asset" in erros


def test_criar_setup_segredo_422(client):
    resp = client.post(
        "/api/setups", json=_payload_setup(origem_asset="https://x.example?token=abc"), headers=_wh()
    )
    assert resp.status_code == 422


def test_criar_maquina_201_e_sem_credencial(client):
    resp = _criar_maquina(client)
    assert resp.status_code == 201
    assert resp.json()["identificacao"] == "203.0.113.99"

    ruim = client.post(
        "/api/maquinas", json={"nome": "srv-bad", "identificacao": "203.0.113.1?token=x"}, headers=_wh()
    )
    assert ruim.status_code == 422


def test_criar_maquina_duplicada_409(client):
    _criar_maquina(client)
    resp = client.post(
        "/api/maquinas", json={"nome": "SRV-API-01", "identificacao": "10.0.0.1"}, headers=_wh()
    )
    assert resp.status_code == 409


# ---------------------------------------------------------------------------
# US2 — Registrar execução via API
# ---------------------------------------------------------------------------

def test_registrar_execucao_201(client, criar_setup, db_engine):
    setup = criar_setup(nome="Setup API Exec", plataforma_alvo="Debian + Docker Swarm")
    maq = _criar_maquina(client).json()

    resp = client.post(
        "/api/execucoes",
        json={"setup_id": setup.id, "target_host_id": maq["id"], "status": "sucesso", "resumo": "ok via API"},
        headers=_wh(),
    )
    assert resp.status_code == 201
    assert resp.json()["setup_id"] == setup.id

    lista = client.get("/api/execucoes", headers={"Authorization": f"Bearer {_read_token()}"})
    assert lista.status_code == 200 and lista.json()["total"] >= 1


def test_registrar_execucao_setup_inexistente_404(client):
    maq = _criar_maquina(client).json()
    resp = client.post(
        "/api/execucoes",
        json={"setup_id": 99999, "target_host_id": maq["id"], "status": "sucesso"},
        headers=_wh(),
    )
    assert resp.status_code == 404


def test_registrar_execucao_maquina_inativa_400(client, criar_setup, db_engine):
    setup = criar_setup(nome="Setup API Exec", plataforma_alvo="Debian + Docker Swarm")
    maq = _criar_maquina(client).json()
    with Session(db_engine) as session:
        host = session.get(TargetHost, maq["id"])
        host.status = "inativa"
        session.add(host)
        session.commit()

    resp = client.post(
        "/api/execucoes",
        json={"setup_id": setup.id, "target_host_id": maq["id"], "status": "sucesso"},
        headers=_wh(),
    )
    assert resp.status_code == 400


def test_registrar_execucao_status_invalido_422(client, criar_setup):
    setup = criar_setup(nome="Setup API Exec", plataforma_alvo="Debian + Docker Swarm")
    maq = _criar_maquina(client).json()
    resp = client.post(
        "/api/execucoes",
        json={"setup_id": setup.id, "target_host_id": maq["id"], "status": "nao-existe"},
        headers=_wh(),
    )
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# US3 — Segurança/escopo
# ---------------------------------------------------------------------------

def test_escrita_sem_token_401(client):
    resp = client.post("/api/setups", json=_payload_setup())
    assert resp.status_code == 401


def test_escrita_com_token_de_leitura_403(client):
    resp = client.post("/api/setups", json=_payload_setup(), headers={"Authorization": f"Bearer {_read_token()}"})
    assert resp.status_code == 403


def test_escrita_sem_env_bloqueada(client, monkeypatch):
    monkeypatch.delenv("AUTOMATIC1_WRITE_API_TOKEN", raising=False)
    resp = client.post("/api/setups", json=_payload_setup(), headers=_wh())
    assert resp.status_code == 401
