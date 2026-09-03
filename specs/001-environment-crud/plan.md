# Implementation Plan: CRUD de Ambientes de Setup (Automatic1)

**Branch**: `001-environment-crud` | **Date**: 2026-09-02 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/001-environment-crud/spec.md`

## Summary

Construir uma ferramenta web de administração interna que cataloga os "setups de ambiente" que o Automatic1 provisiona. **v1 entrega criar + listar** (P1); detalhes (P2), edição (P2) e arquivamento (P3) ficam para slices posteriores da mesma feature, mas o modelo de dados e as rotas já são desenhados para suportá-los. A spec é intencionalmente agnóstica de tecnologia; a stack foi decidida na Fase 0 (pesquisa) com o usuário: **Python 3.11 + FastAPI + SQLModel + SQLite**, com telas server-rendered em Jinja2 e testes com pytest.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: FastAPI (web); SQLModel (ORM = SQLAlchemy + Pydantic); Jinja2 (templates server-rendered); python-multipart (formulários HTML); uvicorn (servidor ASGI). Dev/test: pytest, httpx (TestClient do FastAPI).

**Storage**: SQLite (arquivo local, ex.: `data/setups.db`); schema gerenciado por SQLModel (`create_all`) + bootstrap idempotente; sem segredos no arquivo (apenas registros de catálogo, FR-013).

**Testing**: pytest + TestClient (httpx). Cada teste usa um SQLite temporário (em memória/arquivo tmp) isolado. Test-first obrigatório (constituição III).

**Target Platform**: Navegador moderno — servidor web local em rede interna confiável (ferramenta de administração interna).

**Project Type**: Web application (admin interno) server-rendered, entidade única; sem SPA e sem API pública externa.

**Performance Goals**: Ferramenta interna de baixo volume — ações percebidas < 1s; sem meta de carga no v1.

**Constraints**: SQLite single-writer; concorrência "última gravação vence" (v1, documentado na spec); **sem autenticação no v1** (rede interna confiável; permissões futuras fora do escopo); sem segredos em código/logs (FR-013); mensagens de erro claras e acionáveis (FR-014).

**Scale/Scope**: Poucos administradores internos; dezenas a centenas de registros no v1.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Gates extraídos da constituição (`.specify/memory/constitution.md`) e avaliação:

- **G1 — Test-First (III, NÃO-NEGOCIÁVEL)**: testes escritos antes da implementação, com validação automatizada (pytest) e verificáveis em CI. → Atendido: suíte pytest planejada antes do código de produção; testes em `tests/`.
- **G2 — Automation & Reproducibility (I)**: bootstrap 100% scriptável, idempotente (venv + deps + init DB) via `scripts/*.ps1`. → Atendido: scripts `setup-dev.ps1`, `run.ps1`, `test.ps1`.
- **G3 — Security (IV)**: nenhum segredo em código/logs; dependências pinadas e revisadas; SQLite local sem credenciais. → Atendido: sem secrets; sem auth no v1 por ser rede interna (registrado como premissa da spec).
- **G4 — Simplicity & YAGNI (VII)**: entidade única; sem camadas especulativas (sem repository/service genéricos); sem auth extra no v1. → Atendido: FastAPI + SQLModel direto, validação em Pydantic; sem camada de serviço genérica.
- **G5 — Consistent UX (VI)**: feedback e erros acionáveis (FR-014), estados vazios amigáveis. → Atendido: páginas com mensagens por campo e estados vazios.
- **G6 — Observability & Versioning (VIII)**: logging estruturado das operações de escrita; app versionado (SemVer). → Atendido: logging por request/operação; versão no `pyproject`.

**Resultado**: GATE **PASS** — nenhuma violação identificada; arquitetura mantida mínima. Reavaliado após o design da Fase 1: sem alterações.

## Project Structure

### Documentation (this feature)

```text
specs/001-environment-crud/
├── spec.md              # Especificação da feature
├── plan.md              # Este arquivo (/speckit-plan)
├── research.md          # Fase 0 — decisões técnicas
├── data-model.md        # Fase 1 — modelo de dados
├── quickstart.md        # Fase 1 — guia de validação
├── contracts/           # Fase 1 — contratos (rotas web + validação)
└── tasks.md             # Fase 2 (/speckit-tasks — NÃO criado aqui)
```

### Source Code (repository root)

```text
app/
├── __init__.py
├── main.py              # Criação da app FastAPI + montagem de rotas/templates
├── config.py            # Configurações (caminho do DB, operador, versão)
├── database.py          # Engine/sessão SQLite + init do schema
├── models.py            # SQLModel: EnvironmentSetup
├── schemas.py           # Validação Pydantic (criar/editar) + regras de negócio
├── routers/
│   ├── __init__.py
│   └── web.py           # Páginas: listar, novo/criar, detalhe (+ editar/arquivar futuros)
├── templates/
│   ├── base.html
│   ├── setups/
│   │   ├── list.html
│   │   ├── form.html
│   │   └── detail.html
└── static/
    └── app.css

tests/
├── conftest.py          # Fixtures: DB temporário + TestClient
├── test_create_setup.py # US1 (P1)
└── test_list_setups.py  # US2 (P1)

scripts/
├── setup-dev.ps1        # Bootstrap idempotente (venv, deps, init DB)
├── run.ps1              # Sobe o servidor local
└── test.ps1             # Roda a suíte pytest

requirements.txt         # deps pinadas (runtime)  — ou pyproject.toml
requirements-dev.txt     # deps de teste pinadas
```

**Structure Decision**: Monólito FastAPI **server-rendered** único (não há frontend/backend separados: sem SPA e sem API externa). Entidade única → **sem camada de serviço genérica** (YAGNI): regras de negócio (unicidade de nome, validação SemVer, ausência de segredos) concentradas na validação Pydantic/schemas + helpers no router. Modelo + validação separados (`models.py`/`schemas.py`) preservam a separação entre persistência e regras, facilitando teste unitário das regras.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

Não aplicável — o Constitution Check passou sem violações (G1–G6 atendidos). Nenhuma complexidade extra é introduzida nesta fase.
