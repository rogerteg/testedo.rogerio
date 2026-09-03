"""Testes de listagem de setups — User Story 2 (P1) — spec C5-C7.

Test-First (constituição III): estes testes DEVEM falhar (red) antes da
implementação do core da US2 e passar (green) após ela.
"""
from datetime import datetime, timezone

BASE = "https://github.com/exemplo/setup"


def test_lista_setups(client, criar_setup):
    criar_setup(nome="Dev Box", plataforma_alvo="Windows", origem_asset=BASE)

    resp = client.get("/setups")

    assert resp.status_code == 200
    assert "Dev Box" in resp.text
    assert "Windows" in resp.text


def test_ordena_mais_recente_primeiro(client, criar_setup):
    # C5 — Then registros ordenados do mais recente (updated_at desc) para o mais antigo.
    criar_setup(
        nome="Mais Antigo",
        plataforma_alvo="Linux",
        origem_asset=BASE,
        updated_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
    criar_setup(
        nome="Mais Novo",
        plataforma_alvo="Windows",
        origem_asset=BASE,
        updated_at=datetime(2026, 2, 1, tzinfo=timezone.utc),
    )

    resp = client.get("/setups")

    assert resp.status_code == 200
    assert resp.text.index("Mais Novo") < resp.text.index("Mais Antigo")


def test_filtro_por_nome_ou_plataforma(client, criar_setup):
    # C6 — Given vários registros, When filtra q=linux, Then apenas compatíveis.
    criar_setup(nome="Setup Windows", plataforma_alvo="Windows", origem_asset=BASE)
    criar_setup(nome="Setup Linux", plataforma_alvo="Linux", origem_asset=BASE)

    resp = client.get("/setups", params={"q": "linux"})

    assert resp.status_code == 200
    assert "Setup Linux" in resp.text
    assert "Setup Windows" not in resp.text


def test_busca_sem_resultado(client, criar_setup):
    criar_setup(nome="Dev Box", plataforma_alvo="Windows", origem_asset=BASE)

    resp = client.get("/setups", params={"q": "zzz-inexistente"})

    assert resp.status_code == 200
    assert "Nenhum" in resp.text or "nada encontrado" in resp.text.lower()


def test_estado_vazio(client):
    # C7 — Given nenhum registro, Then estado vazio amigável com CTA de cadastro.
    resp = client.get("/setups")

    assert resp.status_code == 200
    assert "Nenhum" in resp.text
    assert "/setups/novo" in resp.text
