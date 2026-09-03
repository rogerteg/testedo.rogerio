"""Catálogo padrão (stack de referência) que o Automatic1 provisiona — feature 002.

Fonte da ação "Carregar catálogo padrão" (spec/data-model). A carga é **aditiva e
não destrutiva**: apenas cria os itens ausentes (nome único normalizado — FR-004)
e nunca altera/remove registros existentes (FR-005). Nenhuma versão/hash é
inventada (FR-003); a licença é referência inicial conferível no upstream
(constituição IV). Itens com suspeita de segredo não são criados (FR-010).
"""
import logging

from sqlmodel import Session, select

from .models import EnvironmentSetup
from .schemas import contem_segredo, normalizar_nome

logger = logging.getLogger("automatic1_admin.catalogo_padrao")

# Ambiente-alvo suportado (valor controlado — FR-006).
AMBIENTE_PADRAO = "Debian + Docker Swarm"

# Campos de texto sujeitos à checagem anti-segredo na carga (FR-010).
_CAMPOS_TEXTO = ("nome", "descricao", "plataforma_alvo", "origem_asset", "versao", "hash", "licenca")

# Manifesto do catálogo padrão (data-model.md): 7 infraestrutura base + 8 aplicações.
# versao/hash ausentes = "não informado" (upstream usa latest; nada inventado).
CATALOGO_PADRAO: list[dict] = [
    # --- Infraestrutura base (7) -----------------------------------------
    {
        "nome": "Docker Engine",
        "categoria": "infraestrutura_base",
        "plataforma_alvo": AMBIENTE_PADRAO,
        "origem_asset": "https://github.com/moby/moby",
        "descricao": "Motor de containers que sustenta a stack do Automatic1.",
        "licenca": "Apache-2.0",
        "status": "ativo",
    },
    {
        "nome": "Docker Swarm (modo cluster)",
        "categoria": "infraestrutura_base",
        "plataforma_alvo": AMBIENTE_PADRAO,
        "origem_asset": "https://github.com/moby/swarmkit",
        "descricao": "Orquestração em modo cluster nativa do Docker Engine.",
        "licenca": "Apache-2.0",
        "status": "ativo",
    },
    {
        "nome": "Traefik",
        "categoria": "infraestrutura_base",
        "plataforma_alvo": AMBIENTE_PADRAO,
        "origem_asset": "https://github.com/traefik/traefik",
        "descricao": "Proxy reverso e roteador com TLS automático para os serviços.",
        "licenca": "MIT",
        "status": "ativo",
    },
    {
        "nome": "Portainer",
        "categoria": "infraestrutura_base",
        "plataforma_alvo": AMBIENTE_PADRAO,
        "origem_asset": "https://github.com/portainer/portainer",
        "descricao": "Gerenciador visual do Docker/Docker Swarm.",
        "licenca": None,
        "status": "ativo",
    },
    {
        "nome": "PostgreSQL",
        "categoria": "infraestrutura_base",
        "plataforma_alvo": AMBIENTE_PADRAO,
        "origem_asset": "https://github.com/postgres/postgres",
        "descricao": "Banco relacional usado como base de dados da stack.",
        "licenca": "PostgreSQL License",
        "status": "ativo",
    },
    {
        "nome": "MongoDB",
        "categoria": "infraestrutura_base",
        "plataforma_alvo": AMBIENTE_PADRAO,
        "origem_asset": "https://github.com/mongodb/mongo",
        "descricao": "Banco de documentos usado por aplicações da stack.",
        "licenca": None,
        "status": "ativo",
    },
    {
        "nome": "Redis",
        "categoria": "infraestrutura_base",
        "plataforma_alvo": AMBIENTE_PADRAO,
        "origem_asset": "https://github.com/redis/redis",
        "descricao": "Cache/mensageria leve usado pelas aplicações da stack.",
        "licenca": None,
        "status": "ativo",
    },
    # --- Aplicações (8) ---------------------------------------------------
    {
        "nome": "Chatwoot",
        "categoria": "aplicacao",
        "plataforma_alvo": AMBIENTE_PADRAO,
        "origem_asset": "https://github.com/chatwoot/chatwoot",
        "descricao": "Plataforma de atendimento ao cliente (helpdesk/chat).",
        "licenca": "MIT",
        "status": "ativo",
    },
    {
        "nome": "Evolution API",
        "categoria": "aplicacao",
        "plataforma_alvo": AMBIENTE_PADRAO,
        "origem_asset": "https://github.com/EvolutionAPI/evolution-api",
        "descricao": "API para integração com WhatsApp (não oficial).",
        "licenca": "MIT",
        "status": "ativo",
    },
    {
        "nome": "Typebot",
        "categoria": "aplicacao",
        "plataforma_alvo": AMBIENTE_PADRAO,
        "origem_asset": "https://github.com/baptistearno/typebot",
        "descricao": "Editor de conversas/chatbots com fluxos visuais.",
        "licenca": "AGPL-3.0",
        "status": "ativo",
    },
    {
        "nome": "N8N",
        "categoria": "aplicacao",
        "plataforma_alvo": AMBIENTE_PADRAO,
        "origem_asset": "https://github.com/n8n-io/n8n",
        "descricao": "Automação de fluxos de trabalho (workflow automation).",
        "licenca": "Sustainable Use License",
        "status": "ativo",
    },
    {
        "nome": "Appsmith",
        "categoria": "aplicacao",
        "plataforma_alvo": AMBIENTE_PADRAO,
        "origem_asset": "https://github.com/appsmithorg/appsmith",
        "descricao": "Plataforma low-code para construir painéis e apps internos.",
        "licenca": "Apache-2.0",
        "status": "ativo",
    },
    {
        "nome": "MinIO",
        "categoria": "aplicacao",
        "plataforma_alvo": AMBIENTE_PADRAO,
        "origem_asset": "https://github.com/minio/minio",
        "descricao": "Armazenamento de objetos compatível com S3.",
        "licenca": "AGPL-3.0",
        "status": "ativo",
    },
    {
        "nome": "RabbitMQ",
        "categoria": "aplicacao",
        "plataforma_alvo": AMBIENTE_PADRAO,
        "origem_asset": "https://github.com/rabbitmq/rabbitmq-server",
        "descricao": "Mensageria (broker AMQP) para comunicação entre serviços.",
        "licenca": "MPL-2.0",
        "status": "ativo",
    },
    {
        "nome": "PgAdmin4",
        "categoria": "aplicacao",
        "plataforma_alvo": AMBIENTE_PADRAO,
        "origem_asset": "https://github.com/pgadmin-org/pgadmin4",
        "descricao": "Interface de administração do PostgreSQL.",
        "licenca": "PostgreSQL License",
        "status": "ativo",
    },
]


def carregar_catalogo_padrao(session: Session, autor: str) -> dict:
    """Carrega o catálogo padrão de forma **aditiva e não destrutiva** (FR-004/FR-005).

    Para cada item do manifesto:
    - anti-segredo (FR-010): se qualquer campo de texto sinalizar segredo, o item
      **não** é criado e entra em ``avisos``;
    - se já existe setup com o mesmo nome normalizado, é **ignorado** (nunca
      alterado/removido);
    - senão, cria o registro com auditoria (autor) e conta como ``criados``.

    Retorna ``{"criados": int, "ignorados": int, "avisos": list[str]}``.
    """
    existentes = session.exec(select(EnvironmentSetup)).all()
    nomes_existentes = {normalizar_nome(r.nome) for r in existentes}

    criados = 0
    ignorados = 0
    avisos: list[str] = []

    for item in CATALOGO_PADRAO:
        nome = (item.get("nome") or "").strip()
        bloqueado = False
        for campo in _CAMPOS_TEXTO:
            valor = item.get(campo)
            if isinstance(valor, str) and contem_segredo(valor):
                avisos.append(
                    f"{nome}: bloqueado por suspeita de segredo no campo '{campo}' (FR-010)."
                )
                bloqueado = True
                break
        if bloqueado:
            continue

        if normalizar_nome(nome) in nomes_existentes:
            ignorados += 1
            continue

        session.add(
            EnvironmentSetup(
                **item,
                created_by=autor,
                updated_by=autor,
            )
        )
        nomes_existentes.add(normalizar_nome(nome))
        criados += 1

    if criados:
        session.commit()

    logger.info(
        "Catálogo padrão carregado por %s: criados=%s ignorados=%s avisos=%s",
        autor,
        criados,
        ignorados,
        len(avisos),
    )
    return {"criados": criados, "ignorados": ignorados, "avisos": avisos}
