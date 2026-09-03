"""Testes da feature 002 — Catálogo Padrão (stack de referência) — quickstart C1-C7.

Test-First (constituição III): estes testes DEVEM falhar (red) antes da
implementação da rota/UI do catálogo padrão e passar (green) após ela.
"""
from urllib.parse import parse_qs, urlsplit

from sqlmodel import Session, select

from app.catalogo_padrao import (
    AMBIENTE_PADRAO,
    CATALOGO_PADRAO,
    carregar_catalogo_padrao,
)
from app.models import EnvironmentSetup
from app.schemas import normalizar_nome

N_PADRAO = len(CATALOGO_PADRAO)


def _rows(db_engine):
    with Session(db_engine) as session:
        return session.exec(select(EnvironmentSetup)).all()


def _post_e_query(client):
    """POST /setups/carregar-padrao (sem seguir redirect) e devolve a query da location."""
    resp = client.post("/setups/carregar-padrao", follow_redirects=False)
    assert resp.status_code == 303
    return parse_qs(urlsplit(resp.headers["location"]).query)


def _indexar(rows):
    return {normalizar_nome(r.nome): r for r in rows}


# ---------------------------------------------------------------------------
# US1 — Carga inicial + relatório (C1, C2, C7)
# ---------------------------------------------------------------------------

def test_carga_popula_manifesto_completo(client, db_engine):
    # C1 — carga cria a stack padrão completa com plataforma/categoria/origem corretos.
    resp = client.post("/setups/carregar-padrao", follow_redirects=False)
    assert resp.status_code == 303

    rows = _indexar(_rows(db_engine))
    assert len(rows) == N_PADRAO
    for item in CATALOGO_PADRAO:
        r = rows[normalizar_nome(item["nome"])]
        assert r.plataforma_alvo == AMBIENTE_PADRAO
        assert r.status == "ativo"
        assert r.categoria == item["categoria"]
        assert r.origem_asset == item["origem_asset"]
        # C2 — proveniência: versão/hash não inventados (não informado).
        assert r.versao is None
        assert r.hash is None
        assert r.created_by == "admin"  # OPERATOR_NAME default (auditoria)


def test_relatorio_carga_criados_ignorados(client):
    # C1/FR-008 — relatório informa criados e ignorados.
    qs = _post_e_query(client)
    assert qs.get("sucesso") == ["catalogo_carregado"]
    assert int(qs["criados"][0]) == N_PADRAO
    assert int(qs["ignorados"][0]) == 0


def test_mensagem_relatorio_na_listagem(client):
    # FR-008/FR-014 — a listagem exibe o relatório pós-carga.
    resp = client.post("/setups/carregar-padrao", follow_redirects=True)
    assert resp.status_code == 200
    assert "Catálogo padrão carregado" in resp.text
    assert str(N_PADRAO) in resp.text


def test_estado_vazio_oferece_carga_padrao(client):
    # FR-001 — CTA de carga no estado vazio (e botão no cabeçalho).
    resp = client.get("/setups")
    assert resp.status_code == 200
    assert "Carregar catálogo padrão" in resp.text
    assert "/setups/carregar-padrao" in resp.text


def test_anti_segredo_bloqueia_item_do_manifesto(monkeypatch, db_engine):
    # C7/FR-010 — item do manifesto com suspeita de segredo NÃO é criado e vira aviso.
    malicioso = [
        {
            "nome": "Setup Malicioso",
            "categoria": "aplicacao",
            "plataforma_alvo": AMBIENTE_PADRAO,
            "origem_asset": "https://github.com/exemplo/setup?token=abc123",
            "descricao": "item adulterado",
            "licenca": None,
            "status": "ativo",
        }
    ]
    monkeypatch.setattr("app.catalogo_padrao.CATALOGO_PADRAO", malicioso)

    with Session(db_engine) as session:
        relatorio = carregar_catalogo_padrao(session, autor="tester")

    assert relatorio["criados"] == 0
    assert len(relatorio["avisos"]) == 1
    assert _rows(db_engine) == []


# ---------------------------------------------------------------------------
# US3 — Recarga idempotente e não destrutiva (C3, C4)
# ---------------------------------------------------------------------------

def test_recarga_idempotente(client, db_engine):
    # C3 — 2ª carga não duplica: criados=0, ignorados=N.
    _post_e_query(client)
    qs = _post_e_query(client)

    assert int(qs["criados"][0]) == 0
    assert int(qs["ignorados"][0]) == N_PADRAO
    assert len(_rows(db_engine)) == N_PADRAO


def test_recarga_nao_destrutivo_nome_colidindo(client, criar_setup, db_engine):
    # C4 — registro do usuário com nome colidindo (caixa) não é alterado/removido.
    criar_setup(
        nome="n8n",
        plataforma_alvo="Windows",
        origem_asset="https://github.com/exemplo/n8n-custom",
        status="rascunho",
    )

    qs = _post_e_query(client)

    assert int(qs["criados"][0]) == N_PADRAO - 1
    assert int(qs["ignorados"][0]) == 1

    rows = _indexar(_rows(db_engine))
    assert len(rows) == N_PADRAO  # 14 padrão + 1 do usuário (n8n) ocupando o slot
    user = rows[normalizar_nome("n8n")]
    assert user.plataforma_alvo == "Windows"
    assert user.status == "rascunho"
    assert user.categoria is None
    assert user.origem_asset == "https://github.com/exemplo/n8n-custom"


# ---------------------------------------------------------------------------
# US2 — Categoria e ambiente-alvo (C5, C6)
# ---------------------------------------------------------------------------

def test_filtro_categoria_infraestrutura(client, db_engine):
    _post_e_query(client)
    resp = client.get("/setups", params={"categoria": "infraestrutura_base"})
    assert resp.status_code == 200
    assert "Docker Engine" in resp.text
    assert "Chatwoot" not in resp.text


def test_filtro_categoria_aplicacao(client, db_engine):
    _post_e_query(client)
    resp = client.get("/setups", params={"categoria": "aplicacao"})
    assert resp.status_code == 200
    assert "Chatwoot" in resp.text
    assert "Docker Engine" not in resp.text


def test_detalhe_mostra_categoria(client, db_engine):
    _post_e_query(client)
    rows = _rows(db_engine)
    infra = next(r for r in rows if r.categoria == "infraestrutura_base")
    resp = client.get(f"/setups/{infra.id}")
    assert resp.status_code == 200
    assert "Infraestrutura base" in resp.text


def test_registro_manual_sem_categoria_no_detalhe(client, criar_setup):
    # C6 — registro manual aparece como "não classificada", sem erros.
    setup = criar_setup(nome="Meu Setup Manual", plataforma_alvo="Windows")
    resp = client.get(f"/setups/{setup.id}")
    assert resp.status_code == 200
    assert "não classificada" in resp.text
