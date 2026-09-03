"""Testes de edição — User Story 4 (P2, slice futura).

Test-First: DEVEM falhar (red) antes da implementação e passar após ela.
"""
from sqlmodel import Session

from app.models import EnvironmentSetup

BASE = "https://github.com/exemplo/setup"


def _buscar(db_engine, setup_id) -> EnvironmentSetup:
    with Session(db_engine) as session:
        return session.get(EnvironmentSetup, setup_id)


def _dados(nome="Alterado"):
    return {
        "nome": nome,
        "descricao": "Descrição nova",
        "plataforma_alvo": "Linux",
        "origem_asset": BASE,
        "versao": "2.0.0",
        "status": "ativo",
    }


def test_editar_setup(client, db_engine, criar_setup):
    s = criar_setup(nome="Original", plataforma_alvo="Windows", origem_asset=BASE)

    resp = client.post(f"/setups/{s.id}/editar", data=_dados(), follow_redirects=False)

    assert resp.status_code == 303
    assert resp.headers["location"].startswith(f"/setups/{s.id}")
    atualizado = _buscar(db_engine, s.id)
    assert atualizado.nome == "Alterado"
    assert atualizado.plataforma_alvo == "Linux"
    assert atualizado.versao == "2.0.0"


def test_editar_renomear_duplicado_bloqueado(client, db_engine, criar_setup):
    criar_setup(nome="Nome Existente", plataforma_alvo="Windows", origem_asset=BASE)
    b = criar_setup(nome="Outro", plataforma_alvo="Linux", origem_asset=BASE)

    resp = client.post(f"/setups/{b.id}/editar", data=_dados(nome="nome existente"))

    assert resp.status_code == 200  # re-render com erro
    assert "já existe" in resp.text.lower()
    assert _buscar(db_engine, b.id).nome == "Outro"  # sem atualização parcial


def test_editar_atualiza_auditoria(client, db_engine, criar_setup):
    s = criar_setup(nome="Com Auditoria", plataforma_alvo="Windows", origem_asset=BASE)
    antes = _buscar(db_engine, s.id)

    resp = client.post(f"/setups/{s.id}/editar", data=_dados(), follow_redirects=False)

    assert resp.status_code == 303
    depois = _buscar(db_engine, s.id)
    assert depois.updated_by is not None
    assert depois.updated_at >= antes.updated_at


def test_editar_campo_obrigatorio_ausente(client, db_engine, criar_setup):
    s = criar_setup(nome="Valido", plataforma_alvo="Windows", origem_asset=BASE)
    dados = _dados()
    dados.pop("plataforma_alvo")

    resp = client.post(f"/setups/{s.id}/editar", data=dados)

    assert resp.status_code == 200
    assert "obrigatória" in resp.text.lower()
    assert _buscar(db_engine, s.id).plataforma_alvo == "Windows"  # inalterado
