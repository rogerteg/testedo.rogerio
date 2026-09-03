"""Testes da feature 004 — Provisionador Real — quickstart C1-C6.

Test-First (constituição III): DEVEM falhar (red) antes da implementação do
engine/rota e passar (green) após ela. Usa apenas FakeRunner (sem rede/SSH).
"""
import pytest
from sqlmodel import Session, select

from app.models import Execution, TargetHost
from app.provisioner import ProvisionamentoError, montar_comando, provisionar, redigir
from app.runners import FakeRunner, RunResult

ORIGEM_SH = "https://raw.githubusercontent.com/acme/setup/main/install.sh"
ORIGEM_REPO = "https://github.com/acme/setup"


def _host(db_engine, **campos):
    dados = {"nome": "srv-01", "identificacao": "203.0.113.10"}
    dados.update(campos)
    dados.setdefault("status", "ativa")
    with Session(db_engine) as session:
        h = TargetHost(**dados, created_by="admin", updated_by="admin")
        session.add(h)
        session.commit()
        session.refresh(h)
        return h


def _rows_exec(db_engine):
    with Session(db_engine) as session:
        return session.exec(select(Execution)).all()


# ---------------------------------------------------------------------------
# US1/US3 — Engine: sucesso e falha (C1, C2)
# ---------------------------------------------------------------------------

def test_provisionar_sucesso_cria_execucao_real(db_engine, criar_setup):
    setup = criar_setup(nome="Setup .sh", origem_asset=ORIGEM_SH, plataforma_alvo="Debian + Docker Swarm")
    host = _host(db_engine)
    runner = FakeRunner(resultados=[RunResult(exit_code=0, output="Instalado com sucesso.")])

    with Session(db_engine) as session:
        ex = provisionar(session, runner, setup, host, autor="admin")

    assert ex.status == "sucesso"
    assert ex.exit_code == 0
    assert ex.log and "Instalado com sucesso." in ex.log
    assert ex.started_at is not None and ex.finished_at is not None
    assert ex.created_by == "admin"
    assert runner.chamadas and "comando" in runner.chamadas[0]
    assert "install.sh" in runner.chamadas[0]["comando"]


def test_provisionar_falha_grava_erro_com_log(db_engine, criar_setup):
    setup = criar_setup(nome="Setup .sh", origem_asset=ORIGEM_SH, plataforma_alvo="Debian + Docker Swarm")
    host = _host(db_engine)
    runner = FakeRunner(resultados=[RunResult(exit_code=2, output="Falhou: pacote não encontrado")])

    with Session(db_engine) as session:
        ex = provisionar(session, runner, setup, host, autor="admin")

    assert ex.status == "erro"
    assert ex.exit_code == 2
    assert "pacote não encontrado" in (ex.log or "")


# ---------------------------------------------------------------------------
# US3 — Guardas (C3) e integridade/redação (C4, C5)
# ---------------------------------------------------------------------------

def test_guardas_setup_arquivado(db_engine, criar_setup):
    setup = criar_setup(nome="Setup .sh", origem_asset=ORIGEM_SH, plataforma_alvo="Debian + Docker Swarm", status="arquivado")
    host = _host(db_engine)
    runner = FakeRunner()
    with Session(db_engine) as session, pytest.raises(ProvisionamentoError):
        provisionar(session, runner, setup, host, autor="admin")
    assert _rows_exec(db_engine) == []
    assert runner.chamadas == []


def test_guardas_maquina_inativa(db_engine, criar_setup):
    setup = criar_setup(nome="Setup .sh", origem_asset=ORIGEM_SH, plataforma_alvo="Debian + Docker Swarm")
    host = _host(db_engine, status="inativa")
    runner = FakeRunner()
    with Session(db_engine) as session, pytest.raises(ProvisionamentoError):
        provisionar(session, runner, setup, host, autor="admin")
    assert _rows_exec(db_engine) == []


def test_guarda_origem_nao_executavel(db_engine, criar_setup):
    setup = criar_setup(nome="Setup repo", origem_asset=ORIGEM_REPO, plataforma_alvo="Debian + Docker Swarm")
    host = _host(db_engine)
    runner = FakeRunner()
    with Session(db_engine) as session, pytest.raises(ProvisionamentoError):
        provisionar(session, runner, setup, host, autor="admin")
    assert _rows_exec(db_engine) == []


def test_guarda_concorrencia_em_andamento(db_engine, criar_setup):
    setup = criar_setup(nome="Setup .sh", origem_asset=ORIGEM_SH, plataforma_alvo="Debian + Docker Swarm")
    host = _host(db_engine)
    with Session(db_engine) as session:
        session.add(Execution(setup_id=setup.id, target_host_id=host.id, status="em_andamento", created_by="admin"))
        session.commit()
    runner = FakeRunner()
    with Session(db_engine) as session, pytest.raises(ProvisionamentoError):
        provisionar(session, runner, setup, host, autor="admin")
    assert runner.chamadas == []


def test_montar_comando_verifica_hash_quando_presente(db_engine, criar_setup):
    setup = criar_setup(nome="Setup .sh", origem_asset=ORIGEM_SH, plataforma_alvo="Debian + Docker Swarm", hash="abc123def456")
    cmd = montar_comando(setup)
    assert "sha256sum" in cmd
    assert "abc123def456" in cmd


def test_montar_comando_sem_hash_nao_verifica(db_engine, criar_setup):
    setup = criar_setup(nome="Setup .sh", origem_asset=ORIGEM_SH, plataforma_alvo="Debian + Docker Swarm")
    cmd = montar_comando(setup)
    assert "sha256sum" not in cmd


def test_redigir_mascara_segredos():
    saida = "ok; token=abc123; senha=segredo42; chave=x1"
    limpo = redigir(saida, segredos=["segredo42"])
    assert "abc123" not in limpo
    assert "segredo42" not in limpo
    assert "x1" not in limpo
    assert "[REDACTED]" in limpo


# ---------------------------------------------------------------------------
# US2 — Reexecução preserva histórico (C6)
# ---------------------------------------------------------------------------

def test_reexecucao_preserva_historico(db_engine, criar_setup):
    setup = criar_setup(nome="Setup .sh", origem_asset=ORIGEM_SH, plataforma_alvo="Debian + Docker Swarm")
    host = _host(db_engine)
    runner = FakeRunner(
        resultados=[
            RunResult(exit_code=1, output="primeira falhou"),
            RunResult(exit_code=0, output="segunda ok"),
        ]
    )
    with Session(db_engine) as session:
        ex1 = provisionar(session, runner, setup, host, autor="admin")
    with Session(db_engine) as session:
        ex2 = provisionar(session, runner, setup, host, autor="admin")

    assert ex1.status == "erro" and ex2.status == "sucesso"
    rows = _rows_exec(db_engine)
    assert len(rows) == 2  # histórico preservado


# ---------------------------------------------------------------------------
# HTTP — rota de provisionamento (wiring) com FakeRunner
# ---------------------------------------------------------------------------

def test_http_provisionar_sucesso(client, db_engine, criar_setup, monkeypatch):
    monkeypatch.setenv("AUTOMATIC1_RUNNER", "fake")
    setup = criar_setup(nome="Setup .sh", origem_asset=ORIGEM_SH, plataforma_alvo="Debian + Docker Swarm")
    host = _host(db_engine)

    pagina = client.get(f"/setups/{setup.id}/provisionar", params={"maquina": host.id})
    assert pagina.status_code == 200
    assert "Provisionar" in pagina.text
    assert 'name="confirmacao"' in pagina.text

    resp = client.post(
        f"/setups/{setup.id}/provisionar",
        data={"target_host_id": str(host.id), "confirmacao": "sim"},
        follow_redirects=False,
    )
    assert resp.status_code == 303
    rows = _rows_exec(db_engine)
    assert len(rows) == 1
    assert rows[0].status in ("sucesso", "erro")
    assert rows[0].log  # fake preenche log


def test_http_provisionar_sem_credencial_mensagem(client, db_engine, criar_setup, monkeypatch):
    # Sem AUTOMATIC1_RUNNER=fake e sem chave SSH configurada → guarda acionável.
    monkeypatch.delenv("AUTOMATIC1_RUNNER", raising=False)
    monkeypatch.delenv("AUTOMATIC1_SSH_KEY", raising=False)
    setup = criar_setup(nome="Setup .sh", origem_asset=ORIGEM_SH, plataforma_alvo="Debian + Docker Swarm")
    host = _host(db_engine)

    pagina = client.get(f"/setups/{setup.id}/provisionar", params={"maquina": host.id})
    assert pagina.status_code == 200
    assert "AUTOMATIC1_SSH_KEY" in pagina.text
    assert 'name="confirmacao"' not in pagina.text
