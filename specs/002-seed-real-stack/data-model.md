# Data Model: Catálogo Padrão do Automatic1 (stack de referência)

**Branch**: `002-seed-real-stack` | **Date**: 2026-09-03 | **Spec**: [spec.md](spec.md) | **Research**: [research.md](research.md)

## Entity: EnvironmentSetup (Setup de Ambiente) — mudanças aditivas

Base herdada da feature `001` (ver [data-model da 001](../001-environment-crud/data-model.md)). Esta feature **adiciona**:

| Campo | Tipo (impl.) | Obrigatório | Regras / Validação |
|-------|--------------|-------------|--------------------|
| `categoria` | texto (str) | Não | Enum: `infraestrutura_base` \| `aplicacao`. Null = "não classificada" (registros manuais). Preenchido pelo catálogo padrão (FR-007). Migração aditiva em SQLite (research D5). |

Os registros do **catálogo padrão** usam os valores controlados no modelo existente:

- `plataforma_alvo` = `"Debian + Docker Swarm"` (valor controlado e consistente — FR-006). Registros manuais continuam com texto livre.
- `status` = `ativo` (itens que o Automatic1 provisiona; editável pelo admin).
- `origem_asset` = URL do upstream oficial (constituição IV — reuso com fonte registrada, sem copiar conteúdo).
- `versao` / `hash` = **"não informado"** (upstream usa `latest`/rolling; nenhum valor inventado — FR-003).
- `licenca` = preenchida quando bem estabelecida no upstream; senão "não informado" (referência inicial, conferir no upstream — ver manifesto).

### Ciclo de vida / transições

Sem novas transições automáticas. Registros padrão são registros comuns de catálogo: editáveis/arquiváveis como qualquer outro (feature `001`), e a recarga **nunca** os altera/remove (aditivo — FR-005).

## Manifesto do Catálogo Padrão (CATALOGO_PADRAO)

Fonte da carga (`carregar_catálogo padrão`). Cada item gera um `EnvironmentSetup` quando o nome ainda não existe. Itens com nome já existente são **ignorados** (recarga aditiva). N = nome; C = categoria; O = origem do asset (upstream); L = licença (referência inicial — conferir no upstream).

| Nome | C | Origem do asset (upstream) | Licença (referência) |
|------|---|----------------------------|----------------------|
| Docker Engine | infra | https://github.com/moby/moby | Apache-2.0 |
| Docker Swarm (modo cluster) | infra | https://github.com/moby/swarmkit | Apache-2.0 |
| Traefik | infra | https://github.com/traefik/traefik | MIT |
| Portainer | infra | https://github.com/portainer/portainer | *não informado* |
| PostgreSQL | infra | https://github.com/postgres/postgres | PostgreSQL License |
| MongoDB | infra | https://github.com/mongodb/mongo | SSPL-1.0 (Community) |
| Redis | infra | https://github.com/redis/redis | *não informado* |
| Chatwoot | app | https://github.com/chatwoot/chatwoot | MIT |
| Evolution API | app | https://github.com/EvolutionAPI/evolution-api | MIT |
| Typebot | app | https://github.com/baptistearno/typebot | AGPL-3.0 |
| N8N | app | https://github.com/n8n-io/n8n | Sustainable Use License |
| Appsmith | app | https://github.com/appsmithorg/appsmith | Apache-2.0 |
| MinIO | app | https://github.com/minio/minio | AGPL-3.0 |
| RabbitMQ | app | https://github.com/rabbitmq/rabbitmq-server | MPL-2.0 |
| PgAdmin4 | app | https://github.com/pgadmin-org/pgadmin4 | PostgreSQL License |

> **7 infraestrutura base + 8 aplicações = 15 itens.** `versao`/`hash` ficam "não informado" (nada inventado). Licenças marcadas "*não informado*" ficam em aberto para o operador conferir no upstream. Valores de licença são referência inicial editável — a origem do asset é a fonte canônica de verificação.

## Relacionamentos

Nenhum novo. O catálogo padrão não é entidade persistida: é o **manifesto-fonte** (em `app/catalogo_padrao.py`) que gera/ignora registros de `EnvironmentSetup`.
