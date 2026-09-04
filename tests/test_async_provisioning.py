"""Testes da feature 008 — Execução Assíncrona do Provisionamento.

Determinístico: `conftest` define AUTOMATIC1_ASYNC=0; aqui usamos unitários do
worker e, para o fluxo da rota assíncrona, monkeypatch de `enfileirar`.
"""
import pytest
from sqlmodel import Session

from app.models import Execution, TargetHost
from app.provisioner import ProvisionamentoError, concluir_execucao, iniciar_execucao
from app.runners import FakeRunner, RunResult
from app.worker import _recuperar_orfas_em

ORIGEM_SH = "https://raw.githubusercontent.com/acme/setup/main/install.sh"


def _host(db_engine, **campos):
    dados = {"nome": "srv-async-01", "identificacao": "203.0.113.70"}
    dados.update(campos)
    dados.setdefault("status", "ativa")
    with Session(db_engine) as session:
        h = TargetHost(**dados, created_by="admin", updated_by="admin")
        session.add(h)
        session.commit()
        session.refresh(h)
        return h


def _setup(db_engine, criar_setup, **campos):
    return criar_setup(
        nome="Setup Async", origem_asset=ORIGEM_SH, plataforma_alvo="Debian + Docker Swarm", **campos
    )


def test_iniciar_execucao_cria_em_andamento(db_engine, criar_setup):
    setup = _setup(db_engine, criar_setup)
    host = _host(db_engine)
    with Session(db_engine) as session:
        ex = iniciar_execucao(session, setup, host, autor="admin")
    assert ex.status == "em_andamento"
    assert ex.started_at is not None


def test_iniciar_guarda_concorrencia_em_andamento(db_engine, criar_setup):
    setup = _setup(db_engine, criar_setup)
    host = _host(db_engine)
    with Session(db_engine) as session:
        session.add(Execution(setup_id=setup.id, target_host_id=host.id, status="em_andamento", created_by="admin"))
        session.commit()
    with Session(db_engine) as session, pytest.raises(ProvisionamentoError):
        iniciar_execucao(session, setup, host, autor="admin")


def test_concluir_execucao_sucesso_e_erro(db_engine, criar_setup):
    setup = _setup(db_engine, criar_setup)
    host = _host(db_engine)
    runner = FakeRunner(
        resultados=[
            RunResult(exit_code=0, output="deploy ok"),
            RunResult(exit_code=3, output="falhou no deploy"),
        ]
    )
    with Session(db_engine) as session:
        ex1 = iniciar_execucao(session, setup, host, autor="admin")
        ex1 = concluir_execucao(session, runner, ex1.id)
    assert ex1.status == "sucesso" and "deploy ok" in ex1.log

    with Session(db_engine) as session:
        ex2 = iniciar_execucao(session, setup, host, autor="admin")
        ex2 = concluir_execucao(session, runner, ex2.id)
    assert ex2.status == "erro" and ex2.exit_code == 3


def test_recuperar_orfas_marca_erro(db_engine, criar_setup):
    setup = _setup(db_engine, criar_setup)
    host = _host(db_engine)
    with Session(db_engine) as session:
        session.add(Execution(setup_id=setup.id, target_host_id=host.id, status="em_andamento", created_by="admin"))
        session.commit()
        count = _recuperar_orfas_em(session)
    assert count == 1
    with Session(db_engine) as session:
        ex = session.get(Execution, 1)
        assert ex.status == "erro"
        assert "interrompida" in ex.resumo.lower()


def test_rota_assincrona_retorna_imediato(client, db_engine, criar_setup, monkeypatch):
    monkeypatch.setenv("AUTOMATIC1_ASYNC", "1")
    monkeypatch.setenv("AUTOMATIC1_RUNNER", "fake")
    agendados: list[int] = []

    def _fake_enfileirar(execucao_id):
        agendados.append(execucao_id)
        return True

    monkeypatch.setattr("app.routers.web.enfileirar", _fake_enfileirar)

    setup = _setup(db_engine, criar_setup)
    host = _host(db_engine)
    pagina = client.get(f"/setups/{setup.id}/provisionar", params={"maquina": host.id})
    assert pagina.status_code == 200

    resp = client.post(
        f"/setups/{setup.id}/provisionar",
        data={"target_host_id": str(host.id), "confirmacao": "sim"},
        follow_redirects=False,
    )
    assert resp.status_code == 303

    with Session(db_engine) as session:
        ex = session.get(Execution, agendados[0])
        assert ex is not None and ex.status == "em_andamento"  # retorno imediato


def test_detalhe_mostra_auto_refresh_em_andamento(client, db_engine, criar_setup):
    setup = _setup(db_engine, criar_setup)
    host = _host(db_engine)
    with Session(db_engine) as session:
        session.add(Execution(setup_id=setup.id, target_host_id=host.id, status="em_andamento", created_by="admin"))
        session.commit()
    resp = client.get(f"/setups/{setup.id}")
    assert resp.status_code == 200
    assert 'http-equiv="refresh"' in resp.text


def test_api_detalhe_execucao_inclui_log(client, db_engine, criar_setup):
    setup = _setup(db_engine, criar_setup)
    host = _host(db_engine)
    with Session(db_engine) as session:
        ex = Execution(
            setup_id=setup.id, target_host_id=host.id, status="sucesso",
            log="deploy ok (sanitizado)", exit_code=0, created_by="admin",
        )
        session.add(ex)
        session.commit()
        session.refresh(ex)
        ex_id = ex.id

    token = os_getenv_token()
    resp = client.get(f"/api/execucoes/{ex_id}", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["log"] == "deploy ok (sanitizado)"

    faltando = client.get("/api/execucoes/99999", headers={"Authorization": f"Bearer {token}"})
    assert faltando.status_code == 404


def os_getenv_token():
    import os

    return os.environ.get("AUTOMATIC1_API_TOKEN", "")
