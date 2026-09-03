"""Testes da feature 003 — Máquinas Alvo e Execuções — quickstart C1-C7.

Test-First (constituição III): DEVEM falhar (red) antes da implementação
das rotas/UI de máquinas e execuções e passar (green) após ela.
"""
from urllib.parse import urlsplit

from sqlmodel import Session, select

from app.models import Execution, TargetHost

AMBIENTE = "Debian + Docker Swarm"


def _rows(db_engine, modelo):
    with Session(db_engine) as session:
        return session.exec(select(modelo)).all()


def _criar_maquina(client, **campos):
    dados = {"nome": "srv-prod-01", "identificacao": "203.0.113.10"}
    dados.update(campos)
    return client.post("/maquinas", data=dados, follow_redirects=False)


def _criar_execucao(client, setup_id, maquina_id, **campos):
    dados = {"target_host_id": str(maquina_id), "status": "sucesso", "resumo": "Instalado com sucesso."}
    dados.update(campos)
    return client.post(f"/setups/{setup_id}/executar", data=dados, follow_redirects=False)


# ---------------------------------------------------------------------------
# US1 — Máquinas alvo (C1, C2)
# ---------------------------------------------------------------------------

def test_maquina_criar_listar_detalhe(client, db_engine):
    resp = _criar_maquina(client)
    assert resp.status_code == 303

    maquinas = _rows(db_engine, TargetHost)
    assert len(maquinas) == 1
    m = maquinas[0]
    assert m.nome == "srv-prod-01"
    assert m.identificacao == "203.0.113.10"
    assert m.plataforma_alvo == AMBIENTE  # default controlado
    assert m.status == "ativa"

    lista = client.get("/maquinas")
    assert lista.status_code == 200 and "srv-prod-01" in lista.text

    det = client.get(f"/maquinas/{m.id}")
    assert det.status_code == 200
    assert "203.0.113.10" in det.text and AMBIENTE in det.text


def test_maquina_nome_duplicado(client, db_engine):
    _criar_maquina(client, nome="srv-prod-01")
    resp = _criar_maquina(client, nome="SRV-PROD-01")  # caixa diferente

    assert resp.status_code == 200
    assert "nome" in resp.text and "já existe" in resp.text.lower()
    assert len(_rows(db_engine, TargetHost)) == 1


def test_maquina_campo_obrigatorio_ausente(client, db_engine):
    resp = _criar_maquina(client, identificacao="")
    assert resp.status_code == 200
    assert "identificação" in resp.text.lower() or "identificacao" in resp.text.lower()
    assert _rows(db_engine, TargetHost) == []


def test_maquina_anti_segredo(client, db_engine):
    # FR-004/FR-006 — nenhuma credencial é aceita em campos de texto.
    resp = _criar_maquina(client, identificacao="203.0.113.10?token=abc123")
    assert resp.status_code == 200
    assert _rows(db_engine, TargetHost) == []


def test_maquina_formulario_sem_campos_de_credencial(client):
    # FR-004 — nenhum campo de senha/token/chave no formulário.
    resp = client.get("/maquinas/novo")
    assert resp.status_code == 200
    for campo in ("name=\"senha\"", "name=\"password\"", "name=\"token\""):
        assert campo not in resp.text


def test_maquina_editar(client, db_engine):
    _criar_maquina(client)
    m = _rows(db_engine, TargetHost)[0]
    resp = client.post(
        f"/maquinas/{m.id}/editar",
        data={"nome": "srv-prod-02", "identificacao": "203.0.113.20", "descricao": "nó de produção"},
        follow_redirects=False,
    )
    assert resp.status_code == 303
    m2 = _rows(db_engine, TargetHost)[0]
    assert m2.nome == "srv-prod-02"
    assert m2.descricao == "nó de produção"
    assert m2.updated_by == "admin"


# ---------------------------------------------------------------------------
# US3 — Desativar/Reativar máquina (C6) e avisos
# ---------------------------------------------------------------------------

def test_desativar_maquina_sem_execucoes(client, db_engine):
    _criar_maquina(client)
    m = _rows(db_engine, TargetHost)[0]
    resp = client.post(f"/maquinas/{m.id}/desativar", data={"confirmacao": "sim"}, follow_redirects=False)
    assert resp.status_code == 303
    assert _rows(db_engine, TargetHost)[0].status == "inativa"


def test_desativar_exige_confirmacao(client, db_engine):
    _criar_maquina(client)
    m = _rows(db_engine, TargetHost)[0]
    resp = client.post(f"/maquinas/{m.id}/desativar", data={"confirmacao": ""})
    assert resp.status_code == 200  # re-render sem alteração
    assert _rows(db_engine, TargetHost)[0].status == "ativa"


def test_desativar_maquina_aviso_com_execucoes(client, criar_setup, db_engine):
    setup = criar_setup(nome="Setup Exec", plataforma_alvo=AMBIENTE)
    _criar_maquina(client)
    maquina = _rows(db_engine, TargetHost)[0]
    _criar_execucao(client, setup.id, maquina.id)

    pagina = client.get(f"/maquinas/{maquina.id}/desativar")
    assert pagina.status_code == 200
    assert "execu" in pagina.text.lower()  # aviso de utilização ativa
    assert "1" in pagina.text

    resp = client.post(f"/maquinas/{maquina.id}/desativar", data={"confirmacao": "sim"}, follow_redirects=False)
    assert resp.status_code == 303
    assert _rows(db_engine, TargetHost)[0].status == "inativa"


def test_reativar_maquina(client, db_engine):
    _criar_maquina(client)
    m = _rows(db_engine, TargetHost)[0]
    client.post(f"/maquinas/{m.id}/desativar", data={"confirmacao": "sim"}, follow_redirects=False)
    resp = client.post(f"/maquinas/{m.id}/reativar", follow_redirects=False)
    assert resp.status_code == 303
    assert _rows(db_engine, TargetHost)[0].status == "ativa"


# ---------------------------------------------------------------------------
# US2 — Execuções (C3, C7)
# ---------------------------------------------------------------------------

def test_registrar_execucao_e_historico(client, criar_setup, db_engine):
    setup = criar_setup(nome="Setup Exec", plataforma_alvo=AMBIENTE)
    _criar_maquina(client)
    maquina = _rows(db_engine, TargetHost)[0]

    resp = _criar_execucao(client, setup.id, maquina.id, status="sucesso")
    assert resp.status_code == 303
    assert urlsplit(resp.headers["location"]).path == f"/setups/{setup.id}"

    execs = _rows(db_engine, Execution)
    assert len(execs) == 1
    assert execs[0].setup_id == setup.id
    assert execs[0].target_host_id == maquina.id
    assert execs[0].status == "sucesso"
    assert execs[0].created_by == "admin"

    det_setup = client.get(f"/setups/{setup.id}")
    assert "Instalado com sucesso" in det_setup.text  # histórico no setup

    det_maq = client.get(f"/maquinas/{maquina.id}")
    assert "Instalado com sucesso" in det_maq.text  # histórico na máquina


def test_execucao_status_invalido(client, criar_setup, db_engine):
    setup = criar_setup(nome="Setup Exec", plataforma_alvo=AMBIENTE)
    _criar_maquina(client)
    maquina = _rows(db_engine, TargetHost)[0]
    resp = _criar_execucao(client, setup.id, maquina.id, status="nao-existe")
    assert resp.status_code == 200
    assert _rows(db_engine, Execution) == []


def test_execucao_maquina_inexistente(client, criar_setup, db_engine):
    setup = criar_setup(nome="Setup Exec", plataforma_alvo=AMBIENTE)
    resp = _criar_execucao(client, setup.id, 99999)
    assert resp.status_code == 200
    assert _rows(db_engine, Execution) == []


def test_execucao_maquina_inativa_bloqueada(client, criar_setup, db_engine):
    setup = criar_setup(nome="Setup Exec", plataforma_alvo=AMBIENTE)
    _criar_maquina(client)
    maquina = _rows(db_engine, TargetHost)[0]
    client.post(f"/maquinas/{maquina.id}/desativar", data={"confirmacao": "sim"})
    resp = _criar_execucao(client, setup.id, maquina.id)
    assert resp.status_code == 200
    assert _rows(db_engine, Execution) == []


# ---------------------------------------------------------------------------
# Q3=A — Última execução derivada + fallback manual (C4)
# ---------------------------------------------------------------------------

def test_ultima_execucao_derivada(client, criar_setup, db_engine):
    setup = criar_setup(nome="Setup Exec", plataforma_alvo=AMBIENTE)
    _criar_maquina(client)
    maquina = _rows(db_engine, TargetHost)[0]
    _criar_execucao(client, setup.id, maquina.id, status="sucesso", resumo="primeira")
    _criar_execucao(client, setup.id, maquina.id, status="erro", resumo="segunda falhou")

    det = client.get(f"/setups/{setup.id}")
    assert det.status_code == 200
    # Histórico mostra ambas
    assert "primeira" in det.text and "segunda falhou" in det.text
    # Última execução derivada = a mais recente (erro)
    assert "Última execução" in det.text
    assert det.text.index("segunda falhou") < det.text.index("primeira")


def test_fallback_manual_sem_execucao(client, criar_setup):
    # Q3=A — sem execuções, o detalhe mantém a anotação manual da feature 001.
    setup = criar_setup(
        nome="Setup Manual",
        plataforma_alvo="Windows",
        resultado_ultima_execucao="não executado ainda",
    )
    det = client.get(f"/setups/{setup.id}")
    assert det.status_code == 200
    assert "não executado ainda" in det.text


# ---------------------------------------------------------------------------
# US3 — Aviso de utilização ativa no arquivamento (C5)
# ---------------------------------------------------------------------------

def test_arquivar_aviso_com_execucoes(client, criar_setup, db_engine):
    setup = criar_setup(nome="Setup Exec", plataforma_alvo=AMBIENTE)
    _criar_maquina(client)
    maquina = _rows(db_engine, TargetHost)[0]
    _criar_execucao(client, setup.id, maquina.id)

    pagina = client.get(f"/setups/{setup.id}/arquivar")
    assert pagina.status_code == 200
    assert "execu" in pagina.text.lower()  # aviso

    resp = client.post(f"/setups/{setup.id}/arquivar", data={"confirmacao": "sim"}, follow_redirects=False)
    assert resp.status_code == 303
    assert client.get(f"/setups/{setup.id}").status_code == 200  # ainda existe (arquivado)


def test_arquivar_sem_execucoes_sem_aviso(client, criar_setup):
    setup = criar_setup(nome="Setup Simples", plataforma_alvo="Windows")
    pagina = client.get(f"/setups/{setup.id}/arquivar")
    assert pagina.status_code == 200
    assert "utilização ativa" not in pagina.text.lower()
