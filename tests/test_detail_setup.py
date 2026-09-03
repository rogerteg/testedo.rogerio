"""Testes de detalhes — User Story 3 (P2, slice futura).

Test-First: DEVEM falhar (red) antes da implementação e passar após ela.
"""
BASE = "https://github.com/exemplo/setup"


def test_detalhe_mostra_campos(client, criar_setup):
    s = criar_setup(
        nome="Dev Box",
        descricao="Ambiente de desenvolvimento",
        plataforma_alvo="Windows",
        origem_asset=BASE,
        versao="1.2.3",
        licenca="MIT",
    )

    resp = client.get(f"/setups/{s.id}")

    assert resp.status_code == 200
    assert "Dev Box" in resp.text
    assert "Ambiente de desenvolvimento" in resp.text
    assert "Windows" in resp.text
    assert "1.2.3" in resp.text
    assert "MIT" in resp.text


def test_detalhe_campo_opcional_vazio(client, criar_setup):
    s = criar_setup(nome="Sem Opcionais", plataforma_alvo="Linux", origem_asset=BASE)

    resp = client.get(f"/setups/{s.id}")

    assert resp.status_code == 200
    assert "Sem Opcionais" in resp.text
    assert "não informado" in resp.text.lower()


def test_detalhe_inexistente(client):
    resp = client.get("/setups/99999999")

    assert resp.status_code == 404
