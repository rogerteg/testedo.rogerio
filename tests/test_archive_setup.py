"""Testes de arquivamento (exclusão reversível) — User Story 5 (P3, slice futura).

Test-First: DEVEM falhar (red) antes da implementação e passar após ela.
"""
from sqlmodel import Session

from app.models import EnvironmentSetup

BASE = "https://github.com/exemplo/setup"


def _buscar(db_engine, setup_id) -> EnvironmentSetup:
    with Session(db_engine) as session:
        return session.get(EnvironmentSetup, setup_id)


def test_arquivar_requer_confirmacao(client, db_engine, criar_setup):
    s = criar_setup(nome="Sem Confirmação", plataforma_alvo="Windows", origem_asset=BASE, status="ativo")

    # Cancelamento/ausência de confirmação: nada muda.
    resp = client.post(f"/setups/{s.id}/arquivar", data={})

    assert resp.status_code == 200
    assert _buscar(db_engine, s.id).status == "ativo"


def test_arquivar_com_confirmacao_sai_da_listagem(client, db_engine, criar_setup):
    s = criar_setup(nome="Para Arquivar", plataforma_alvo="Windows", origem_asset=BASE, status="ativo")

    resp = client.post(f"/setups/{s.id}/arquivar", data={"confirmacao": "sim"}, follow_redirects=False)

    assert resp.status_code == 303
    assert _buscar(db_engine, s.id).status == "arquivado"

    lista = client.get("/setups")
    assert lista.status_code == 200
    assert "Para Arquivar" not in lista.text  # fora da listagem ativa


def test_arquivado_permanece_recuperavel(client, db_engine, criar_setup):
    s = criar_setup(nome="Recuperável", plataforma_alvo="Linux", origem_asset=BASE, status="ativo")

    client.post(f"/setups/{s.id}/arquivar", data={"confirmacao": "sim"})

    assert _buscar(db_engine, s.id).status == "arquivado"
    detalhe = client.get(f"/setups/{s.id}")
    assert detalhe.status_code == 200  # registro ainda acessível (auditável/recuperável)
