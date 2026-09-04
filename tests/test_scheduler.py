"""Testes da feature 012 — Rotina/Agendamento (cron) de Execuções.

Cobre: validação cron (5 campos), expressao_casa, vencidos_em (1×/janela),
executar_vencidos (guardas reusadas, worker 008) e CRUD web + "Verificar agora".
Test-first (constituição III).
"""
from datetime import UTC, datetime

from sqlmodel import Session, select

from app.agendador import executar_vencidos, expressao_casa, validar_cron, vencidos_em
from app.models import Agendamento, Execution, TargetHost

ORIGEM_SH = "https://raw.githubusercontent.com/acme/setup/main/install.sh"


def _setup(db_engine, criar_setup, **campos):
    campos.setdefault("status", "ativo")
    return criar_setup(nome="N8N", origem_asset=ORIGEM_SH, plataforma_alvo="Debian + Docker Swarm", **campos)


def _maquina(db_engine, **campos):
    dados = {"nome": "srv-cron", "identificacao": "203.0.113.40"}
    dados.update(campos)
    dados.setdefault("status", "ativa")
    with Session(db_engine) as session:
        m = TargetHost(**dados, created_by="admin", updated_by="admin")
        session.add(m)
        session.commit()
        session.refresh(m)
        return m


def _agendamento(db_engine, setup, maquina, cron="* * * * *", ativo=True):
    with Session(db_engine) as session:
        a = Agendamento(
            setup_id=setup.id, target_host_id=maquina.id, cron=cron,
            ativo=ativo, created_by="admin", updated_by="admin",
        )
        session.add(a)
        session.commit()
        session.refresh(a)
        return a


def _rows(db_engine, modelo):
    with Session(db_engine) as session:
        return session.exec(select(modelo)).all()


# ---------------------------------------------------------------------------
# US1 — Validação cron (FR-001)
# ---------------------------------------------------------------------------

def test_validar_cron_aceita_expressoes_validas():
    assert validar_cron("* * * * *") is None
    assert validar_cron("*/5 * * * *") is None
    assert validar_cron("0 9 * * 1,3,5") is None
    assert validar_cron("30 14 1,15 * *") is None


def test_validar_cron_rejeita_invalidas():
    assert validar_cron("") is not None
    assert validar_cron("* * * *") is not None       # só 4 campos
    assert validar_cron("60 * * * *") is not None     # minuto > 59
    assert validar_cron("* * * * 7") is not None      # dia-semana > 6
    assert validar_cron("abc * * * *") is not None
    assert validar_cron("*/0 * * * *") is not None    # passo inválido


def test_expressao_casa():
    agora = datetime(2026, 9, 4, 14, 30, 0, tzinfo=UTC)  # sexta-feira (weekday 4)
    assert expressao_casa("30 14 4 9 *", agora) is True
    assert expressao_casa("0 14 4 9 *", agora) is False   # minuto não casa
    assert expressao_casa("* * * * 5", agora) is True     # cron 5 = sexta-feira
    assert expressao_casa("* * * * 0", agora) is False    # cron 0 = domingo


def test_expressao_casa_mapeia_dia_semana_cron_para_python():
    # 2026-09-04 é sexta-feira → Python weekday()=4 → cron dia 5 (sexta).
    agora = datetime(2026, 9, 4, 10, 0, 0, tzinfo=UTC)
    assert agora.weekday() == 4
    assert expressao_casa("* * * * 5", agora) is True   # cron 5 = sexta
    assert expressao_casa("* * * * 4", agora) is False  # cron 4 = quinta
    assert expressao_casa("* * * * 1", agora) is False  # cron 1 = segunda


# ---------------------------------------------------------------------------
# US2 — vencidos_em / executar_vencidos
# ---------------------------------------------------------------------------

def test_vencidos_em_casa_no_minuto(db_engine, criar_setup):
    setup = _setup(db_engine, criar_setup)
    maquina = _maquina(db_engine)
    _agendamento(db_engine, setup, maquina, cron="* * * * *")

    agora = datetime(2026, 9, 4, 14, 30, 0, tzinfo=UTC)
    with Session(db_engine) as session:
        vencidos = vencidos_em(session, agora)
    assert len(vencidos) == 1
    assert vencidos[0].setup_id == setup.id


def test_vencidos_em_filtra_inativos_e_fora_do_minuto(db_engine, criar_setup):
    setup = _setup(db_engine, criar_setup)
    maquina = _maquina(db_engine)
    _agendamento(db_engine, setup, maquina, cron="0 3 * * *")   # fora do minuto atual
    _agendamento(db_engine, setup, maquina, cron="* * * * *", ativo=False)

    agora = datetime(2026, 9, 4, 14, 30, 0, tzinfo=UTC)
    with Session(db_engine) as session:
        assert vencidos_em(session, agora) == []


def test_executar_vencidos_1x_por_janela(db_engine, criar_setup, monkeypatch):
    setup = _setup(db_engine, criar_setup)
    maquina = _maquina(db_engine)
    _agendamento(db_engine, setup, maquina, cron="* * * * *")

    fila: list[int] = []
    monkeypatch.setattr("app.agendador.provisionamento_assincrono", lambda: True)
    monkeypatch.setattr("app.agendador.enfileirar", lambda eid: fila.append(eid))

    agora = datetime(2026, 9, 4, 14, 30, 0, tzinfo=UTC)
    with Session(db_engine) as session:
        assert executar_vencidos(session, autor="admin", agora=agora) == 1
        # segunda chamada no mesmo minuto → não repete
        assert executar_vencidos(session, autor="admin", agora=agora) == 0

    assert len(fila) == 1
    execucoes = _rows(db_engine, Execution)
    assert len(execucoes) == 1
    assert execucoes[0].status == "em_andamento"


def test_executar_vencidos_respeita_guarda_setup_arquivado(db_engine, criar_setup, monkeypatch):
    setup = _setup(db_engine, criar_setup, status="arquivado")
    maquina = _maquina(db_engine)
    _agendamento(db_engine, setup, maquina, cron="* * * * *")

    fila: list[int] = []
    monkeypatch.setattr("app.agendador.provisionamento_assincrono", lambda: True)
    monkeypatch.setattr("app.agendador.enfileirar", lambda eid: fila.append(eid))

    agora = datetime(2026, 9, 4, 14, 30, 0, tzinfo=UTC)
    with Session(db_engine) as session:
        assert executar_vencidos(session, autor="admin", agora=agora) == 0
    assert fila == []
    assert _rows(db_engine, Execution) == []


# ---------------------------------------------------------------------------
# US3 — CRUD web + "Verificar agora"
# ---------------------------------------------------------------------------

def test_web_criar_agendamento(client, db_engine, criar_setup):
    setup = _setup(db_engine, criar_setup)
    maquina = _maquina(db_engine)
    resp = client.post(
        "/agendamentos",
        data={
            "setup_id": str(setup.id),
            "target_host_id": str(maquina.id),
            "cron": "0 6 * * *",
        },
        follow_redirects=False,
    )
    assert resp.status_code == 303
    agenda = _rows(db_engine, Agendamento)
    assert len(agenda) == 1
    assert agenda[0].cron == "0 6 * * *"


def test_web_criar_agendamento_cron_invalido(client, db_engine, criar_setup):
    setup = _setup(db_engine, criar_setup)
    maquina = _maquina(db_engine)
    resp = client.post(
        "/agendamentos",
        data={
            "setup_id": str(setup.id),
            "target_host_id": str(maquina.id),
            "cron": "99 * * * *",
        },
    )
    assert resp.status_code == 200
    assert "cron" in resp.text.lower() or "inválida" in resp.text.lower()
    assert _rows(db_engine, Agendamento) == []


def test_web_verificar_agora_dispara(client, db_engine, criar_setup):
    setup = _setup(db_engine, criar_setup)
    maquina = _maquina(db_engine)
    _agendamento(db_engine, setup, maquina, cron="* * * * *")

    # ASYNC=0 no conftest + sem runner → executar_vencidos marca erro (síncrono),
    # mas ainda dispara (cria Execution e atualiza ultimo_disparo).
    resp = client.post("/agendamentos/verificar", follow_redirects=False)
    assert resp.status_code == 303
    execucoes = _rows(db_engine, Execution)
    assert len(execucoes) == 1


def test_web_agendamentos_lista(client, db_engine, criar_setup):
    setup = _setup(db_engine, criar_setup)
    maquina = _maquina(db_engine)
    _agendamento(db_engine, setup, maquina)
    resp = client.get("/agendamentos")
    assert resp.status_code == 200
    assert "N8N" in resp.text


def test_web_toggle_ativo(client, db_engine, criar_setup):
    setup = _setup(db_engine, criar_setup)
    maquina = _maquina(db_engine)
    agenda = _agendamento(db_engine, setup, maquina)
    resp = client.post(f"/agendamentos/{agenda.id}/desativar", follow_redirects=False)
    assert resp.status_code == 303
    a = _rows(db_engine, Agendamento)[0]
    assert a.ativo is False
