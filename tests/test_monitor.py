"""Testes da feature 011 — Monitoramento/Status dos Serviços (leitura).

Cobre: comando somente leitura, consulta web com FakeRunner (saída sanitizada),
guardas (inativa/sem runner) e API de leitura (200/400/404/503). Test-first.
"""
from sqlmodel import Session

from app.models import TargetHost
from app.monitor import consultar_status, montar_comando_status
from app.runners import FakeRunner, RunResult

SAIDA_OK = "ID  HOSTNAME  STATUS\nxxx node1  Ready\nd9p  n8n  replicated  1/1"


def _maquina(db_engine, **campos):
    dados = {"nome": "srv-status", "identificacao": "203.0.113.30"}
    dados.update(campos)
    dados.setdefault("status", "ativa")
    with Session(db_engine) as session:
        m = TargetHost(**dados, created_by="admin", updated_by="admin")
        session.add(m)
        session.commit()
        session.refresh(m)
        return m


# ---------------------------------------------------------------------------
# US1 — Comando e consulta (D1/D2)
# ---------------------------------------------------------------------------

def test_montar_comando_status_somente_leitura():
    cmd = montar_comando_status()
    assert "docker node ls" in cmd
    assert "docker service ls" in cmd
    # Não pode conter operação destrutiva/instalação.
    assert "rm -rf" not in cmd
    assert "curl" not in cmd


def test_consultar_status_sucesso():
    runner = FakeRunner(resultados=[RunResult(exit_code=0, output=SAIDA_OK)])
    resultado = consultar_status(runner, host="203.0.113.30")
    assert resultado["ok"] is True
    assert resultado["exit_code"] == 0
    assert "n8n" in resultado["saida"]
    assert runner.chamadas and "docker service ls" in runner.chamadas[0]["comando"]


def test_consultar_status_erro_transporte(monkeypatch):
    class RunnerErro:
        def executar(self, *, comando, host, timeout=0):
            raise RuntimeError("timeout ssh")

    resultado = consultar_status(RunnerErro(), host="203.0.113.30")
    assert resultado["ok"] is False
    assert "ERRO no transporte" in resultado["saida"]


def test_consultar_status_redige_segredo():
    runner = FakeRunner(
        resultados=[RunResult(exit_code=0, output="token=abc123\nok")]
    )
    resultado = consultar_status(runner, host="203.0.113.30")
    assert "abc123" not in resultado["saida"]


# ---------------------------------------------------------------------------
# US1 — Rota web
# ---------------------------------------------------------------------------

def test_web_status_maquina_ativa_fake(client, db_engine, monkeypatch):
    monkeypatch.setenv("AUTOMATIC1_RUNNER", "fake")
    _maquina(db_engine)
    resp = client.get("/maquinas/1/status")
    assert resp.status_code == 200
    assert "docker service ls" in resp.text or "sucesso" in resp.text.lower()


def test_web_status_maquina_inativa(client, db_engine, monkeypatch):
    monkeypatch.setenv("AUTOMATIC1_RUNNER", "fake")
    _maquina(db_engine, status="inativa")
    resp = client.get("/maquinas/1/status")
    assert resp.status_code == 200
    assert "inativa" in resp.text.lower()


def test_web_status_sem_runner(client, db_engine):
    _maquina(db_engine)
    resp = client.get("/maquinas/1/status")
    assert resp.status_code == 200
    assert "AUTOMATIC1_SSH_KEY" in resp.text


# ---------------------------------------------------------------------------
# US2 — API de leitura
# ---------------------------------------------------------------------------

def test_api_status_sucesso(client, db_engine, monkeypatch):
    monkeypatch.setenv("AUTOMATIC1_RUNNER", "fake")
    _maquina(db_engine)
    resp = client.get(
        "/api/maquinas/1/status",
        headers={"Authorization": "Bearer token-de-teste"},
    )
    assert resp.status_code == 200
    corpo = resp.json()
    assert corpo["status"] == "sucesso"
    assert "docker service ls" in resp.text or "saida" in corpo


def test_api_status_sem_token(client, db_engine):
    _maquina(db_engine)
    resp = client.get("/api/maquinas/1/status")
    assert resp.status_code == 401


def test_api_status_maquina_inexistente(client, db_engine, monkeypatch):
    monkeypatch.setenv("AUTOMATIC1_RUNNER", "fake")
    resp = client.get(
        "/api/maquinas/999/status",
        headers={"Authorization": "Bearer token-de-teste"},
    )
    assert resp.status_code == 404


def test_api_status_maquina_inativa(client, db_engine, monkeypatch):
    monkeypatch.setenv("AUTOMATIC1_RUNNER", "fake")
    _maquina(db_engine, status="inativa")
    resp = client.get(
        "/api/maquinas/1/status",
        headers={"Authorization": "Bearer token-de-teste"},
    )
    assert resp.status_code == 400
