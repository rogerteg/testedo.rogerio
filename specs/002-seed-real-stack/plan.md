# Implementation Plan: Catálogo Padrão do Automatic1 (002-seed-real-stack)

**Branch**: `002-seed-real-stack` | **Date**: 2026-09-03 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/002-seed-real-stack/spec.md`

## Summary

Evoluir o **Automatic1 Admin** (feature `001`, CRUD de setups) para um catálogo com **conteúdo real**: uma ação "**Carregar catálogo padrão**" insere a stack de referência que o Automatic1 provisiona em Debian + Docker Swarm — **7 infraestrutura base + 8 aplicações** — com proveniência (origem do asset no upstream, licença quando conhecida; versão/hash "não informado" — nada inventado, constituição IV). A carga é **aditiva e não destrutiva** (nunca altera/remove existentes; idempotente). O modelo ganha o campo **`categoria`** (infra vs aplicação) e a listagem/detalhe passam a exibir e filtrar por categoria/ambiente-alvo. **Provisionamento/execução continua fora do escopo** (FR-011).

## Technical Context

**Language/Version**: Python 3.11+ (mesma da feature `001`).

**Primary Dependencies**: FastAPI (web); SQLModel (ORM); Jinja2 (templates); sem dependências novas (nenhuma lib de seed/licença necessária — manifesto em código Python).

**Storage**: SQLite local (`data/setups.db`). Mudança aditiva: nova coluna nullable `categoria` via `create_all` + **migração aditiva idempotente** (PRAGMA + `ALTER TABLE ADD COLUMN`) em `init_db()` (research D5).

**Testing**: pytest + TestClient (mesmas fixtures da feature `001`). Test-first (constituição III). Suíte nova em `tests/test_catalogo_padrao.py` (C1–C7).

**Target Platform**: Navegador moderno — ferramenta de administração interna em rede confiável (server-rendered, Jinja2).

**Project Type**: Web application (admin interno) server-rendered; monólito FastAPI único.

**Performance Goals**: Baixo volume (dezenas–centenas de registros; 15 itens na carga). Carga percebida < 1s.

**Constraints**: Idempotência e não-destrutividade da carga (FR-004/FR-005); regra anti-segredo aplicada à carga (FR-010); sem auth no v1 (`OPERATOR_NAME` para auditoria); sem inventar versão/hash (FR-003); sem execução/provisionamento (FR-011).

**Scale/Scope**: Poucos administradores; 15 registros padrão + registros manuais existentes.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Gates extraídos da constituição (`.specify/memory/constitution.md`):

- **G1 — Test-First (III, NÃO-NEGOCIÁVEL)**: testes antes da implementação, validação automatizada (pytest/CI). → Atendido: `tests/test_catalogo_padrao.py` escrito antes do core (red-green); CI existente roda pytest.
- **G2 — Automation & Reproducibility (I)**: bootstrap scriptável/idempotente; migração aditiva idempotente. → Atendido: `init_db()` com PRAGMA+ALTER; scripts `setup-dev.ps1`/`test.ps1` já existentes.
- **G3 — Security (IV)**: nenhum segredo; assets upstream reutilizados **por referência** (origem), não copiados; conteúdo do manifesto passa por anti-segredo. → Atendido: `origem_asset` = URL do upstream; FR-010/SC-005.
- **G4 — Simplicity & YAGNI (VII)**: sem nova entidade/camada especulativa; sem libs novas; recarga aditiva (sem proveniência/histórico ainda). → Atendido: apenas campo `categoria` + manifesto em código + rota.
- **G5 — Consistent UX (VI)**: relatório claro pós-carga (criados/ignorados/avisos), CTA/estado vazio, PT-BR. → Atendido (FR-008/FR-014).
- **G6 — Observability & Versioning (VIII)**: logging estruturado da carga; app SemVer. → Atendido: log com contagens por operação.

**Resultado**: GATE **PASS** — sem violações; arquitetura mantida mínima. Reavaliado após a Fase 1: sem alterações (design aditivo confirmado).

## Key Design Decisions (resumo — detalhe em research.md)

1. **Carga por ação explícita**: `POST /setups/carregar-padrao` (CTA estado vazio + botão no cabeçalho) → `303` com relatório (D1).
2. **Recarga estritamente aditiva**: adiciona ausentes; nunca altera/remove existentes; idempotente (D2).
3. **`categoria`** (enum nullable) no modelo + valor controlado `"Debian + Docker Swarm"` em `plataforma_alvo` nos registros padrão (D3).
4. **Manifesto em código** (`app/catalogo_padrao.py`): 15 itens (7 infra + 8 apps) com origem no upstream; versão/hash "não informado"; licença melhor esforço (D4).
5. **Migração aditiva** idempotente da coluna `categoria` no `init_db()` (D5).
6. **Anti-segredo na carga** (D6) e **auditoria** com operador configurado (D8).

## Project Structure

### Documentation (this feature)

```text
specs/002-seed-real-stack/
├── spec.md              # Especificação da feature
├── plan.md              # Este arquivo (/speckit-plan)
├── research.md          # Fase 0 — decisões técnicas
├── data-model.md        # Fase 1 — modelo de dados (+ manifesto padrão)
├── quickstart.md        # Fase 1 — guia de validação
├── contracts/           # Fase 1 — contratos web
└── tasks.md             # Fase 2 (/speckit-tasks — NÃO criado aqui)
```

### Source Code (repository root)

```text
app/
├── models.py            # + campo categoria (nullable)
├── schemas.py           # + CATEGORIA_VALIDOS/CATEGORIA_LABEL (validação)
├── catalogo_padrao.py   # NOVO — manifesto CATALOGO_PADRAO + carregar_catalogo_padrao()
├── database.py          # init_db: create_all + migração aditiva (PRAGMA+ALTER)
├── routers/
│   └── web.py           # POST /setups/carregar-padrao; GET /setups com ?categoria= e mensagem de relatório
└── templates/
    ├── setups/
    │   ├── list.html    # coluna Categoria + filtro categoria + botão/CTA "Carregar catálogo padrão"
    │   └── detail.html  # linha Categoria
tests/
├── conftest.py          # (existente) — sem mudanças estruturais
├── test_catalogo_padrao.py  # NOVO — C1–C7 (US1–US3)
scripts/                 # (existentes)
```

**Structure Decision**: Mantém o monólito FastAPI server-rendered da feature `001`. O manifesto/carga do catálogo padrão fica em um módulo dedicado (`app/catalogo_padrao.py`) separado das rotas — dados controlados + lógica de carga testável isoladamente; o router só expõe a ação e a UI. Sem camada de serviço genérica (YAGNI).

## Complexity Tracking

> Sem violações de constituição a justificar — GATE PASS sem ressalvas. A migração aditiva (`PRAGMA`+`ALTER`) é a única "complexidade" de schema e é justificada por preservar bancos existentes da feature `001` sem introduzir ferramenta de migração (YAGNI).
