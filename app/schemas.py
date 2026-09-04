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

# Categorias do catálogo (feature 002) — data-model.md; rótulos PT-BR.
CATEGORIA_VALIDOS = {"infraestrutura_base", "aplicacao"}
CATEGORIA_LABEL = {
    "infraestrutura_base": "Infraestrutura base",
    "aplicacao": "Aplicação",
}

# SemVer: MAJOR.MINOR.PATCH [+ pre-release] [+ build]  (FR-003)
SEMVER_RE = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
    r"(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
)

# Feature 009 — config de deploy por setup (domínio/vars).
# Linha válida: CHAVE=valor, chave [A-Z_][A-Z0-9_]* (sem segredo).
_VARIAVEL_DEPLOY_LINHA = re.compile(r"^([A-Z_][A-Z0-9_]*)=(.*)$")
VARIAVEIS_DEPLOY_LIMITE = 4000
DOMINIO_LIMITE = 255


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

# Limite máximo de caracteres dos campos opcionais (models.py / data-model.md) — T041.
LIMITES_OPCIONAIS = {
    "descricao": 2000,
    "versao": 64,
    "hash": 256,
    "licenca": 500,
    "resultado_ultima_execucao": 1000,
}

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


def rotulo_categoria(valor: str | None) -> str:
    """Rótulo PT-BR de categoria; None/vazio → 'não classificada' (feature 002)."""
    if not valor:
        return "não classificada"
    return CATEGORIA_LABEL.get(valor, valor)


def parse_variaveis_deploy(texto: str | None) -> list[tuple[str, str]]:
    """Retorna pares ``(CHAVE, valor)`` das linhas válidas (feature 009).

    Linhas inválidas ou vazias são ignoradas (validação estrita fica no
    ``validar_campos``). Usado pelo provisionador p/ montar os ``export``.
    """
    pares: list[tuple[str, str]] = []
    for linha in (texto or "").splitlines():
        m = _VARIAVEL_DEPLOY_LINHA.match(linha.strip())
        if m:
            pares.append((m.group(1), m.group(2)))
    return pares


def validar_deploy(dados: dict) -> dict:
    """Valida os campos de config de deploy (feature 009).

    Retorna ``{campo: mensagem}`` para ``dominio``/``variaveis_deploy``
    (vazio = válido). Sem segredos (FR-013/constituição IV); chaves no formato
    ``[A-Z_][A-Z0-9_]*``; valores sem quebras de linha embutidas.
    """
    erros: dict = {}

    dominio = (dados.get("dominio") or "").strip()
    if dominio:
        if len(dominio) > DOMINIO_LIMITE:
            erros["dominio"] = f"O domínio deve ter no máximo {DOMINIO_LIMITE} caracteres."
        elif contem_segredo(dominio):
            erros["dominio"] = (
                "Não são permitidos segredos/credenciais no domínio; informe apenas "
                "o domínio público (FR-013)."
            )

    variaveis = (dados.get("variaveis_deploy") or "")
    if variaveis:
        if len(variaveis) > VARIAVEIS_DEPLOY_LIMITE:
            erros["variaveis_deploy"] = (
                f"As variáveis devem ter no máximo {VARIAVEIS_DEPLOY_LIMITE} caracteres."
            )
        else:
            for linha in variaveis.splitlines():
                linha = linha.strip()
                if not linha:
                    continue
                m = _VARIAVEL_DEPLOY_LINHA.match(linha)
                if not m:
                    erros["variaveis_deploy"] = (
                        "Cada linha deve estar no formato CHAVE=valor, com chave "
                        "em MAIÚSCULAS (ex.: AUTOMATIC1_N8N_DOMAIN=n8n.exemplo.com)."
                    )
                    break
                if contem_segredo(linha):
                    erros["variaveis_deploy"] = (
                        "Não são permitidos segredos/credenciais nas variáveis de "
                        "deploy; informe apenas parâmetros não secretos (FR-013)."
                    )
                    break
                # Valor não pode ter quebra de linha embutida (linha única).
                if "\n" in m.group(2) or "\r" in m.group(2):
                    erros["variaveis_deploy"] = (
                        "Valores com quebras de linha não são permitidos."
                    )
                    break

    return erros



def contem_segredo(texto: str) -> bool:
    """True se o texto contiver sinais de segredo/credencial (FR-013/SC-005)."""
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
    if versao:
        if len(versao) > 64:
            erros["versao"] = "A versão deve ter no máximo 64 caracteres."
        elif not SEMVER_RE.match(versao):
            erros["versao"] = "Versão inválida. Use o formato SemVer (ex.: 1.2.3 ou 1.2.3-rc.1)."

    status = (dados.get("status") or "rascunho").strip()
    if status not in STATUS_VALIDOS:
        erros["status"] = "Status inválido."

    # Limites máximos dos campos opcionais de texto livre (T041 / models.py).
    rotulos = {
        "descricao": "A descrição",
        "hash": "O hash",
        "licenca": "A licença",
        "resultado_ultima_execucao": "O resultado da última execução",
    }
    for campo, limite in LIMITES_OPCIONAIS.items():
        if campo == "versao":
            continue  # versao já validada acima (limite + SemVer)
        valor = (dados.get(campo) or "").strip()
        if len(valor) > limite:
            erros[campo] = f"{rotulos[campo]} deve ter no máximo {limite} caracteres."

    for campo in CAMPOS_TEXTO:
        valor = dados.get(campo)
        if isinstance(valor, str) and contem_segredo(valor):
            erros[campo] = (
                "Não são permitidos segredos/credenciais neste campo; informe apenas "
                "referências ou placeholders (FR-013)."
            )

    # Feature 009 — config de deploy por setup (domínio/vars, sem segredos).
    erros.update(validar_deploy(dados))

    return erros


# ---------------------------------------------------------------------------
# Feature 003 — Máquinas alvo e execuções
# ---------------------------------------------------------------------------

# Estados de máquina (data-model.md) e rótulos PT-BR.
HOST_STATUS_VALIDOS = {"ativa", "inativa"}
HOST_STATUS_LABEL = {
    "ativa": "Ativa",
    "inativa": "Inativa",
}

# Estados de execução (data-model.md) e rótulos PT-BR.
EXEC_STATUS_VALIDOS = {"planejada", "em_andamento", "sucesso", "erro", "cancelada"}
EXEC_STATUS_LABEL = {
    "planejada": "Planejada",
    "em_andamento": "Em andamento",
    "sucesso": "Sucesso",
    "erro": "Erro",
    "cancelada": "Cancelada",
}

# Campos de texto de máquina sujeitos à regra anti-segredo (FR-004/FR-006).
_CAMPOS_MAQUINA_TEXTO = ("nome", "identificacao", "plataforma_alvo", "descricao")


def validar_maquina(dados: dict) -> dict:
    """Valida os campos de uma máquina alvo (feature 003).

    Retorna ``{campo: mensagem}`` (vazio = válido). Nenhuma credencial aceita.
    """
    erros: dict = {}

    nome = (dados.get("nome") or "").strip()
    identificacao = (dados.get("identificacao") or "").strip()
    plataforma = (dados.get("plataforma_alvo") or "").strip()
    status = (dados.get("status") or "ativa").strip()

    if not nome:
        erros["nome"] = "O nome é obrigatório."
    elif len(nome) > 120:
        erros["nome"] = "O nome deve ter no máximo 120 caracteres."

    if not identificacao:
        erros["identificacao"] = "A identificação/endereço é obrigatória."
    elif len(identificacao) > 255:
        erros["identificacao"] = "A identificação deve ter no máximo 255 caracteres."

    if plataforma and len(plataforma) > 60:
        erros["plataforma_alvo"] = "A plataforma alvo deve ter no máximo 60 caracteres."

    if status not in HOST_STATUS_VALIDOS:
        erros["status"] = "Status inválido."

    descricao = (dados.get("descricao") or "").strip()
    if len(descricao) > 1000:
        erros["descricao"] = "A descrição deve ter no máximo 1000 caracteres."

    for campo in _CAMPOS_MAQUINA_TEXTO:
        valor = dados.get(campo)
        if isinstance(valor, str) and contem_segredo(valor):
            erros[campo] = (
                "Não são permitidos segredos/credenciais neste campo; informe apenas "
                "referências ou placeholders (FR-004)."
            )

    return erros


def validar_execucao(dados: dict) -> dict:
    """Valida os campos de uma execução (feature 003).

    A existência/atividade da máquina e do setup é checada na camada de rota
    (depende do banco). Retorna ``{campo: mensagem}`` (vazio = válido).
    """
    erros: dict = {}

    status = (dados.get("status") or "").strip()
    if status not in EXEC_STATUS_VALIDOS:
        erros["status"] = "Status de execução inválido."

    resumo = (dados.get("resumo") or "").strip()
    if len(resumo) > 1000:
        erros["resumo"] = "O resumo deve ter no máximo 1000 caracteres."
    if resumo and contem_segredo(resumo):
        erros["resumo"] = (
            "Não são permitidos segredos/credenciais no resumo; informe apenas "
            "referências ou placeholders (FR-004)."
        )

    return erros
