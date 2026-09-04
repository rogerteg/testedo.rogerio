"""Testes da feature 009 — Config de Deploy por Setup (domínio/vars).

Cobre: validação de `dominio`/`variaveis_deploy` (anti-segredo), injeção de
`export` no `montar_comando` (D2), fluxo web (form criar/editar) e API de
escrita (007). Test-first (constituição III).
"""
from app.models import EnvironmentSetup
from app.provisioner import montar_comando
from app.schemas import validar_campos

ORIGEM_SH = "https://raw.githubusercontent.com/acme/setup/main/install.sh"

CONFIG_VALIDA = "AUTOMATIC1_N8N_DOMAIN=n8n.exemplo.com\nAUTOMATIC1_N8N_VERSION=latest"


def _dados_base(**extra):
    dados = {
        "nome": "N8N",
        "plataforma_alvo": "Debian + Docker Swarm",
        "origem_asset": ORIGEM_SH,
        "status": "ativo",
    }
    dados.update(extra)
    return dados


def _setup(db_engine, criar_setup, **campos):
    campos.setdefault("dominio", "n8n.exemplo.com")
    campos.setdefault("variaveis_deploy", CONFIG_VALIDA)
    return criar_setup(nome="N8N", origem_asset=ORIGEM_SH, plataforma_alvo="Debian + Docker Swarm", **campos)


# ---------------------------------------------------------------------------
# US1 — Validação (schemas.validar_campos)
# ---------------------------------------------------------------------------

def test_config_valida_dominio_e_variaveis():
    assert validar_campos(_dados_base(dominio="n8n.exemplo.com", variaveis_deploy=CONFIG_VALIDA)) == {}


def test_dominio_opcional():
    assert validar_campos(_dados_base(dominio="", variaveis_deploy="")) == {}


def test_variaveis_rejeita_segredo():
    erros = validar_campos(_dados_base(variaveis_deploy="AUTOMATIC1_SENHA=123456"))
    assert "variaveis_deploy" in erros


def test_variaveis_rejeita_linha_sem_igual():
    erros = validar_campos(_dados_base(variaveis_deploy="NAO_EH_CHAVE_VALOR"))
    assert "variaveis_deploy" in erros


def test_variaveis_rejeita_chave_invalida():
    erros = validar_campos(_dados_base(variaveis_deploy="1CHAVE=valor"))
    assert "variaveis_deploy" in erros


def test_dominio_rejeita_segredo():
    erros = validar_campos(_dados_base(dominio="token.abc"))
    assert "dominio" in erros


# ---------------------------------------------------------------------------
# US2 — Injeção no montar_comando (D2)
# ---------------------------------------------------------------------------

def test_montar_comando_exporta_config(db_engine, criar_setup):
    setup = _setup(db_engine, criar_setup)
    cmd = montar_comando(setup)
    assert "export AUTOMATIC1_DOMAIN='n8n.exemplo.com'" in cmd
    assert "export AUTOMATIC1_N8N_DOMAIN='n8n.exemplo.com'" in cmd
    assert "export AUTOMATIC1_N8N_VERSION='latest'" in cmd


def test_montar_comando_sem_config_nao_exporta(db_engine, criar_setup):
    setup = criar_setup(nome="N8N", origem_asset=ORIGEM_SH, plataforma_alvo="Debian + Docker Swarm")
    cmd = montar_comando(setup)
    assert "export " not in cmd
    assert "curl -fsSL" in cmd


def test_montar_comando_exporta_so_dominio(db_engine, criar_setup):
    setup = criar_setup(
        nome="N8N",
        origem_asset=ORIGEM_SH,
        plataforma_alvo="Debian + Docker Swarm",
        dominio="n8n.exemplo.com",
    )
    cmd = montar_comando(setup)
    assert "export AUTOMATIC1_DOMAIN='n8n.exemplo.com'" in cmd
    assert cmd.count("export ") == 1


# ---------------------------------------------------------------------------
# US3 — Fluxo web + API (integração)
# ---------------------------------------------------------------------------

def test_web_criar_setup_com_config(client, db_engine):
    dados = _dados_base(dominio="n8n.exemplo.com", variaveis_deploy=CONFIG_VALIDA)
    resp = client.post("/setups", data=dados, follow_redirects=False)
    assert resp.status_code == 303
    with __import__("sqlmodel").Session(db_engine) as session:
        s = session.exec(__import__("sqlmodel").select(EnvironmentSetup)).one()
        assert s.dominio == "n8n.exemplo.com"
        assert "AUTOMATIC1_N8N_VERSION" in (s.variaveis_deploy or "")


def test_web_rejeita_config_com_segredo(client, db_engine):
    dados = _dados_base(variaveis_deploy="AUTOMATIC1_SENHA=123456")
    resp = client.post("/setups", data=dados, follow_redirects=False)
    assert resp.status_code == 200
    assert "variaveis_deploy" in resp.text or "segredo" in resp.text.lower()


def test_api_write_aceita_config(client):
    payload = {
        "nome": "N8N API",
        "plataforma_alvo": "Debian + Docker Swarm",
        "origem_asset": ORIGEM_SH,
        "status": "ativo",
        "dominio": "n8n.exemplo.com",
        "variaveis_deploy": "AUTOMATIC1_N8N_VERSION=latest",
    }
    resp = client.post(
        "/api/setups",
        json=payload,
        headers={"Authorization": "Bearer token-escrita-teste"},
    )
    assert resp.status_code == 201
    corpo = resp.json()
    assert corpo["dominio"] == "n8n.exemplo.com"
    assert corpo["variaveis_deploy"] == "AUTOMATIC1_N8N_VERSION=latest"


def test_api_write_rejeita_config_com_segredo(client):
    payload = {
        "nome": "N8N API X",
        "plataforma_alvo": "Debian + Docker Swarm",
        "origem_asset": ORIGEM_SH,
        "status": "ativo",
        "variaveis_deploy": "AUTOMATIC1_SENHA=123456",
    }
    resp = client.post(
        "/api/setups",
        json=payload,
        headers={"Authorization": "Bearer token-escrita-teste"},
    )
    assert resp.status_code == 422
