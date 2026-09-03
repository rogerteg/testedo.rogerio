# Data Model / Artefatos: Instalador Próprio do Automatic1

**Branch**: `005-installer` | **Date**: 2026-09-03 | **Spec**: [spec.md](spec.md) | **Research**: [research.md](research.md)

**Sem mudança de entidade/schema** no banco (features `001`–`004` intactas). Esta feature entrega **artefatos de código shell** no repo.

## Estrutura do instalador (no repo)

```text
installer/
├── install.sh          # Entrada/orquestrador (headless): config + bootstrap + apps + manifesto
├── lib/
│   └── common.sh       # Helpers: log, erro, require_root, config env, idempotência (estado), manifesto
├── bootstrap.sh        # Infra base idempotente: Docker + Swarm + Traefik + Portainer + serviços de apoio
├── apps/
│   └── <ferramenta>.sh # Um instalador por app (adoção incremental; apps de referência no v1)
└── config.example.env  # Variáveis de ambiente suportadas (AUTOMATIC1_*) com defaults seguros
```

## Configuração (headless — Q3=A)

| Variável | Default | Descrição |
|----------|---------|-----------|
| `AUTOMATIC1_STATE_DIR` | `/var/lib/automatic1` | Marcadores de idempotência/manifesto |
| `AUTOMATIC1_BOOTSTRAP` | `1` | Executa bootstrap da infra base |
| `AUTOMATIC1_APPS` | `""` | Lista de apps a instalar (ex.: `n8n chatwoot`) |
| `AUTOMATIC1_DOMAIN` | `""` | Domínio base (Traefik/TLS) |
| `AUTOMATIC1_TRAEFIK_EMAIL` | `""` | Email ACME (Let's Encrypt) |
| `AUTOMATIC1_DRY_RUN` | `0` | `1` = valida pré-requisitos sem aplicar mudanças (`--check`) |

## Contrato de saída

- **Exit codes**: `0` sucesso; `1` erro genérico; `2` pré-requisito ausente; `3` config inválida.
- **Manifesto** (stdout + `$AUTOMATIC1_STATE_DIR/manifesto.txt`): linha por item instalado — `serviço | versão | url` — legível/auditável (SC-005).

## Relação com o catálogo

Quando os scripts estiverem **hospedados** (repo publicado), o catálogo (`002`) referenciará cada instalador como `origem_asset` (rastreabilidade/versão/hash — FR-006), destravando o provisionador (`004`). No v1 desta feature isso fica documentado (não apontamos para URLs inexistentes).
