"""Testes de criação de setup — User Story 1 (P1) — spec C1-C4.

Test-First (constituição III): estes testes DEVEM falhar (red) antes da
implementação do core da US1 e passar (green) após ela.
"""
from sqlmodel import Session, func, select

from app.models import EnvironmentSetup


def _total_setups(db_engine) -> int:
    with Session(db_engine) as session:
        return session.exec(select(func.count(EnvironmentSetup.id))).one()


def _dados_validos(**extra):
    dados = {
        "nome": "Dev Box",
        "descricao": "Ambiente de desenvolvimento padrão",
        "plataforma_alvo": "Windows",
        "origem_asset": "https://github.com/exemplo/setup",
        "versao": "1.2.3",
        "licenca": "MIT",
        "status": "ativo",
    }
    dados.update(extra)
    return dados


def test_criar_setup_valido(client, db_engine):
    # C1 — Given campos obrigatórios válidos, When confirma, Then registro persistido
    # e redirect para a listagem (303) com sinal de sucesso.
    resp = client.post("/setups", data=_dados_validos(), follow_redirects=False)

    assert resp.status_code == 303
    assert resp.headers["location"].startswith("/setups")
    assert "sucesso" in resp.headers["location"]
    assert _total_setups(db_engine) == 1


def test_nome_duplicado_bloqueado(client, db_engine, criar_setup):
    # C2 — Given nome já existente (variação de caixa/espaços), When confirma,
    # Then erro claro e NENHUM registro duplicado.
    criar_setup(nome="Dev Box", plataforma_alvo="Windows", origem_asset="https://a")

    resp = client.post("/setups", data=_dados_validos(nome="  dev  box  "))

    assert resp.status_code == 200  # re-render do formulário com erro
    assert "já existe" in resp.text.lower()
    assert _total_setups(db_engine) == 1  # sem duplicata


def test_campo_obrigatorio_ausente(client, db_engine):
    # C3 — Given falta plataforma_alvo, When confirma, Then erro por campo e sem registro.
    dados = _dados_validos()
    dados.pop("plataforma_alvo")

    resp = client.post("/setups", data=dados)

    assert resp.status_code == 200
    assert "plataforma alvo é obrigatória" in resp.text.lower()
    assert _total_setups(db_engine) == 0


def test_versao_invalida(client, db_engine):
    # C4 — Given versão fora do padrão SemVer, When confirma, Then erro explicando o formato.
    resp = client.post("/setups", data=_dados_validos(versao="1.2"))

    assert resp.status_code == 200
    assert "SemVer" in resp.text or "formato" in resp.text
    assert _total_setups(db_engine) == 0


def test_segredo_rejeitado(client, db_engine):
    # FR-013 — Given origem com credencial, When confirma, Then erro e sem registro.
    resp = client.post("/setups", data=_dados_validos(origem_asset="https://x/token=abc123"))

    assert resp.status_code == 200
    assert "segredos" in resp.text.lower()
    assert _total_setups(db_engine) == 0


def test_dados_preservados_no_erro(client, db_engine):
    # FR-004 — Given erro de validação, Then formulário preserva os dados preenchidos.
    resp = client.post("/setups", data=_dados_validos(versao="ruim", descricao="Texto mantido"))

    assert resp.status_code == 200
    assert "Texto mantido" in resp.text
