# Implementation Plan: Autenticação e API REST (006-auth-api)

**Branch**: `006-auth-api` | **Date**: 2026-09-03 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/006-auth-api/spec.md`

## Summary

Adicionar **autenticação** ao Automatic1 Admin (web) e uma **API REST de leitura** para consumo externo. Senha única (`AUTOMATIC1_ADMIN_PASSWORD`) + **cookie de sessão assinado com expiração** (`itsdangerous`); **middleware** protege todas as rotas web (exceto login/logout/health/static); API `/api/*` (setups/maquinas/execucoes) autenticada por **token** (`AUTOMATIC1_API_TOKEN`, Bearer), **somente leitura**. Autoria das escritas mantém `OPERATOR_NAME` (Q3=A). Nada de segredo em banco/logs; sem senha/token → bloqueio claro (FR-007). Regressão `001`–`005` mantida autenticando o `client` default no `conftest`.

## Technical Context

**Language/Version**: Python 3.11+ (mesma stack).

**Primary Dependencies**: FastAPI; **`itsdangerous`** (novo — assinatura/expiração do cookie de sessão; pinado); Jinja2; SQLModel.

**Storage**: SQLite (sem novas entidades). Sessão/token **não persistidos** (ambiente).

**Testing**: pytest + TestClient. Novo `tests/test_auth_api.py` (login/logout/proteção/API/FR-007). `conftest` passa a autenticar o client default (login) para preservar regressão `001`–`005`.

**Target Platform**: Navegador moderno (admin interno) + consumidores HTTP da API.

**Project Type**: Web application (admin interno) server-rendered + API REST (leitura).

**Performance Goals**: Login < 2s; chamadas API < 1s (baixo volume).

**Constraints**: Segredos por ambiente e lidos por requisição (IV); comparação segura; cookie `HttpOnly`/`SameSite=Lax`; API sem segredos nas respostas; autoria `OPERATOR_NAME` (Q3=A); sem senha/token → bloqueio (FR-007).

**Scale/Scope**: Um operador (sem gestão de usuários no v1); API somente leitura.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **G1 — Test-First (III)**: testes de auth/API antes do core; regressão autenticada. → Atendido.
- **G2 — Automation & Reproducibility (I)**: segredos por ambiente; sem alteração de bootstrap. → Atendido.
- **G3 — Security (IV)**: senha/token/segredo **nunca** no banco/repo/log; comparação segura; cookie assinado/expiração. → Atendido.
- **G4 — Simplicity & YAGNI (VII)**: um operador; API read-only; sem gestão de usuários/OAuth. → Atendido.
- **G5 — Consistent UX (VI)**: login/logout claros, mensagens acionáveis, `next` preservado, PT-BR. → Atendido.
- **G6 — Observability & Versioning (VIII)**: log de tentativas inválidas (sem detalhes); SemVer. → Atendido.

**Resultado**: GATE **PASS** — sem violações.

## Key Design Decisions (resumo — research.md)

1. Sessão + senha única via ambiente (Q1=A); cookie assinado `itsdangerous` com TTL — D1.
2. API **somente leitura** por token Bearer (Q2=A) — D2.
3. Autoria mantém `OPERATOR_NAME` (Q3=A) — D3.
4. Segredos lidos por requisição (`app/auth.py`); bloqueio sem config — D4.
5. `conftest` autentica client default; suíte existente continua verde — D5.
6. `app/auth.py`, `app/routers/api.py`, middleware em `main.py`, `login.html`; dep `itsdangerous` — D6.

## Project Structure

### Documentation (this feature)

```text
specs/006-auth-api/
├── spec.md / plan.md / research.md / data-model.md / quickstart.md
├── contracts/{web,api}.md
└── tasks.md   # Fase 2 (/speckit-tasks — NÃO criado aqui)
```

### Source Code (repository root)

```text
app/
├── auth.py                # NOVO — senha/sessão/token (env por requisição; itsdangerous)
├── routers/
│   ├── web.py             # + GET/POST /login, GET /logout
│   └── api.py             # NOVO — GET /api/{setups,maquinas,execucoes} (token)
├── main.py                # + middleware de sessão (rotas protegidas)
├── templates/
│   ├── login.html         # NOVO — formulário de login
│   └── base.html          # + link de logout (quando autenticado)
tests/
├── conftest.py            # client default autenticado (login)
└── test_auth_api.py       # NOVO — C1–C4 (US1–US3)
```

**Structure Decision**: Continua o monólito server-rendered. Helpers de auth isolados (`app/auth.py`); API em router próprio (`api.py`); proteção transversal via middleware (cobre rotas atuais e futuras).

## Complexity Tracking

> Sem violações a justificar — GATE PASS. Nova dependência `itsdangerous` justificada (cookie assinado com expiração, D1).
