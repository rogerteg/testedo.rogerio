"""Testes da feature 010 — Backup/Exportação do Catálogo (JSON).

Cobre: snapshot completo com meta + coleções (execuções com nomes), importação
aditiva (duplicados ignorados), rejeição de segredo, e rotas web
(exportar/importar). Test-first (constituição III).
"""
import json

from sqlmodel import Session, SQLModel, create_engine, select
from sqlmodel.pool import StaticPool

from app.backup import (
    BackupError,
    importar_snapshot,
    montar_snapshot,
    snapshot_para_json,
)
from app.models import EnvironmentSetup, Execution, TargetHost

ORIGEM_SH = "https://raw.githubusercontent.com/acme/setup/main/install.sh"


def _novo_engine():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return engine


def _setup(db_engine, criar_setup, nome="N8N", **campos):
    campos.setdefault("status", "ativo")
    return criar_setup(nome=nome, origem_asset=ORIGEM_SH, plataforma_alvo="Debian + Docker Swarm", **campos)


def _maquina(db_engine, nome="srv-01"):
    with Session(db_engine) as session:
        m = TargetHost(nome=nome, identificacao="203.0.113.10", status="ativa",
                       created_by="admin", updated_by="admin")
        session.add(m)
        session.commit()
        session.refresh(m)
        return m


def _execucao(db_engine, setup, maquina, status="sucesso"):
    with Session(db_engine) as session:
        e = Execution(setup_id=setup.id, target_host_id=maquina.id, status=status,
                      resumo="deploy ok", created_by="admin")
        session.add(e)
        session.commit()
        session.refresh(e)
        return e


def _contar(db_engine, modelo):
    with Session(db_engine) as session:
        return len(session.exec(select(modelo)).all())


# ---------------------------------------------------------------------------
# US1 — Snapshot / exportação
# ---------------------------------------------------------------------------

def test_montar_snapshot_inclui_meta_e_colecoes(db_engine, criar_setup):
    setup = _setup(db_engine, criar_setup)
    maquina = _maquina(db_engine)
    _execucao(db_engine, setup, maquina)

    with Session(db_engine) as session:
        snap = montar_snapshot(session)

    assert snap["formato"] == "automatic1-catalogo"
    assert snap["versao"] == 1
    assert snap["exportado_em"] and snap["por"]
    assert len(snap["setups"]) == 1
    assert len(snap["maquinas"]) == 1
    assert len(snap["execucoes"]) == 1
    ex = snap["execucoes"][0]
    assert ex["setup_nome"] == "N8N"
    assert ex["maquina_nome"] == "srv-01"


def test_snapshot_serializacao_json_valido(db_engine, criar_setup):
    _setup(db_engine, criar_setup, nome="MinIO")
    with Session(db_engine) as session:
        snap = montar_snapshot(session)
    texto = snapshot_para_json(snap)
    assert json.loads(texto)["formato"] == "automatic1-catalogo"


# ---------------------------------------------------------------------------
# US2 — Importação aditiva (Q2=A)
# ---------------------------------------------------------------------------

def test_importar_em_banco_vazio_restaura(db_engine, criar_setup):
    setup = _setup(db_engine, criar_setup)
    maquina = _maquina(db_engine)
    _execucao(db_engine, setup, maquina)
    with Session(db_engine) as session:
        snap = montar_snapshot(session)

    # Novo engine (banco vazio) — importa tudo.
    novo = _novo_engine()
    with Session(novo) as session:
        rel = importar_snapshot(session, snap, autor="restaurador")

    assert rel["criados_setups"] == 1
    assert rel["criadas_maquinas"] == 1
    assert rel["criadas_execucoes"] == 1
    assert _contar(novo, EnvironmentSetup) == 1
    assert _contar(novo, TargetHost) == 1
    assert _contar(novo, Execution) == 1


def test_importar_aditivo_ignora_duplicados(db_engine, criar_setup):
    setup = _setup(db_engine, criar_setup)
    maquina = _maquina(db_engine)
    _execucao(db_engine, setup, maquina)
    with Session(db_engine) as session:
        snap = montar_snapshot(session)
    # Banco já tem os mesmos itens → tudo ignorado.
    with Session(db_engine) as session:
        rel = importar_snapshot(session, snap, autor="admin")
    assert rel["criados_setups"] == 0
    assert rel["ignorados_setups"] == 1
    assert rel["criadas_maquinas"] == 0
    assert rel["ignoradas_maquinas"] == 1
    assert rel["criadas_execucoes"] == 0
    assert rel["ignoradas_execucoes"] == 1
    assert _contar(db_engine, EnvironmentSetup) == 1


def test_importar_rejeita_snapshot_com_segredo(db_engine):
    snap = {
        "formato": "automatic1-catalogo",
        "versao": 1,
        "setups": [{"nome": "Com segredo", "plataforma_alvo": "Debian + Docker Swarm",
                    "origem_asset": ORIGEM_SH, "status": "ativo",
                    "variaveis_deploy": "AUTOMATIC1_SENHA=123456"}],
        "maquinas": [],
        "execucoes": [],
    }
    with Session(db_engine) as session:
        rel = importar_snapshot(session, snap, autor="admin")
    assert rel["invalidos_setups"] == 1
    assert rel["criados_setups"] == 0
    assert _contar(db_engine, EnvironmentSetup) == 0


def test_importar_erro_formato_invalido(db_engine):
    with Session(db_engine) as session, __import__("pytest").raises(BackupError):
        importar_snapshot(session, {"formato": "outro", "versao": 9}, autor="admin")


# ---------------------------------------------------------------------------
# US1/US2 — Rotas web (exportar/importar)
# ---------------------------------------------------------------------------

def test_web_exportar_retorna_json(client, db_engine, criar_setup):
    _setup(db_engine, criar_setup, nome="Typebot")
    resp = client.get("/backup/exportar")
    assert resp.status_code == 200
    assert "application/json" in resp.headers["content-type"]
    dados = resp.json()
    assert dados["formato"] == "automatic1-catalogo"
    assert len(dados["setups"]) == 1


def test_web_importar_restaura_banco_vazio(client, db_engine, criar_setup):
    setup = _setup(db_engine, criar_setup)
    maquina = _maquina(db_engine)
    _execucao(db_engine, setup, maquina)
    with Session(db_engine) as session:
        snap = montar_snapshot(session)
    conteudo = snapshot_para_json(snap).encode("utf-8")

    resp = client.post(
        "/backup/importar",
        files={"arquivo": ("catalogo.json", conteudo, "application/json")},
    )
    assert resp.status_code == 200
    assert "Backup importado" in resp.text
    # Itens já existiam → aditivo: criados == 0 e nada duplicado.
    assert _contar(db_engine, EnvironmentSetup) == 1
    assert _contar(db_engine, Execution) == 1
