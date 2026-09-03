"""Regras de validação e normalização do catálogo (data-model.md / contracts/web.md).

Funções puras e testáveis; a checagem de unicidade de nome depende do banco e
é feita na camada de rota (app/routers/web.py).
"""
import re

# Estados permitidos (data-model.md) e rótulos de exibição (PT-BR).
STATUS_VALIDOS = {"rascunho", "ativo", "com_erro", "arquivado"}
STATUS_LABEL = {
    "rascunho": "Rascunho",
    "ativo": "Ativo",
    "com_erro": "Com erro",
    "arquivado": "Arquivado",
}

# SemVer: MAJOR.MINOR.PATCH [+ pre-release] [+ build]  (FR-003)
SEMVER_RE = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
    r"(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
)

# Campos de texto livre sujeitos à regra anti-segredo (FR-013).
CAMPOS_TEXTO = (
    "nome",
    "descricao",
    "plataforma_alvo",
    "origem_asset",
    "versao",
    "hash",
    "licenca",
    "resultado_ultima_execucao",
)

_SINAIS_SEGREDO = (
    "senha",
    "password",
    "passwd",
    "secret",
    "token",
    "apikey",
    "api_key",
    "access_key",
    "credential",
)


def normalizar_nome(nome: str) -> str:
    """Nome normalizado para unicidade — caixa/whitespace-insensitive (FR-002)."""
    return " ".join(nome.split()).lower()


def _contem_segredo(texto: str) -> bool:
    baixo = texto.lower()
    return any(sinal in baixo for sinal in _SINAIS_SEGREDO)


def validar_campos(dados: dict) -> dict:
    """Valida os campos recebidos de formulário.

    Retorna um dicionário ``{campo: mensagem_de_erro}`` (vazio = dados válidos).
    """
    erros: dict = {}

    nome = (dados.get("nome") or "").strip()
    plataforma = (dados.get("plataforma_alvo") or "").strip()
    origem = (dados.get("origem_asset") or "").strip()

    if not nome:
        erros["nome"] = "O nome é obrigatório."
    elif len(nome) > 120:
        erros["nome"] = "O nome deve ter no máximo 120 caracteres."

    if not plataforma:
        erros["plataforma_alvo"] = "A plataforma alvo é obrigatória."
    elif len(plataforma) > 60:
        erros["plataforma_alvo"] = "A plataforma alvo deve ter no máximo 60 caracteres."

    if not origem:
        erros["origem_asset"] = "A origem do asset é obrigatória."
    elif len(origem) > 500:
        erros["origem_asset"] = "A origem do asset deve ter no máximo 500 caracteres."

    versao = (dados.get("versao") or "").strip()
    if versao and not SEMVER_RE.match(versao):
        erros["versao"] = "Versão inválida. Use o formato SemVer (ex.: 1.2.3 ou 1.2.3-rc.1)."

    status = (dados.get("status") or "rascunho").strip()
    if status not in STATUS_VALIDOS:
        erros["status"] = "Status inválido."

    for campo in CAMPOS_TEXTO:
        valor = dados.get(campo)
        if isinstance(valor, str) and _contem_segredo(valor):
            erros[campo] = (
                "Não são permitidos segredos/credenciais neste campo; informe apenas "
                "referências ou placeholders (FR-013)."
            )

    return erros
