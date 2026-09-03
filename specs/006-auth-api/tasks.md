---

description: "Task list for Autenticação e API REST (006-auth-api)"
---

# Tasks: Autenticação e API REST

**Input**: Design documents from `specs/006-auth-api/`

**Status**: ✅ **Concluído** — `tests/test_auth_api.py` verde (9 testes) + regressão completa autenticada (**96 passed, 4 skip**) + `ruff` limpo.

## Format: `[ID] [P?] [Story] Description`

## Path Conventions

- **Single project (FastAPI monólito)**: `app/`, `tests/` na raiz.

---

## Phase 1: Foundation (Blocking)

- [x] T001 [FOUND] `itsdangerous` pinado (`pyproject.toml` + `uv sync`)
- [x] T002 [P] [FOUND] `app/auth.py` (senha/sessão/token por env; `hmac.compare_digest`; `URLSafeTimedSerializer`)
- [x] T003 [P] [FOUND] `app/routers/api.py` (token Bearer; `GET /api/{setups,maquinas,execucoes}` JSON)

**Checkpoint**: Fundação pronta.

---

## Phase 2: Testes

- [x] T004 [P] [US1/US3] `tests/test_auth_api.py` — login sem env bloqueia; proteção sem sessão; login/logout
- [x] T005 [P] [US2] Testes de API (sem token 401; Bearer válido 200; inválido 401)
- [x] T006 [FOUND] `tests/conftest.py` — ambiente de auth + client default autenticado (regressão 001–005 verde)

**Checkpoint**: Vermelho confirmado antes do core.

---

## Phase 3: User Story 1/3 - Auth web + proteção (P1) 🎯

- [x] T007 [US1/US3] `GET/POST /login` e `GET /logout` em `app/routers/web.py` (cookie HttpOnly/SameSite=Lax; `next` sanitizado; bloqueio sem env)
- [x] T008 [P] [US1] Template `app/templates/login.html` (standalone)
- [x] T009 [US1/US3] Middleware de sessão em `app/main.py` (públicos: login/logout/healthz/static/api)
- [x] T010 [P] [US1] Link "Sair" no `base.html`

**Checkpoint**: Auth web funcional.

---

## Phase 4: User Story 2 - API REST (P1)

- [x] T011 [US2] `api.router` registrado em `main.py`; filtros (`q`/`categoria`/`setup_id`/`maquina_id`)

**Checkpoint**: API funcional.

---

## Phase 5: Polish & Cross-Cutting

- [x] T012 `quickstart.md` (C1–C4) + `pytest` completo verde (96) + `ruff` limpo
- [x] T013 [P] Documentação no `README.md` (variáveis de auth/API, seção feature 006)
- [x] T014 Revisão de segurança (segredos por ambiente; cookie assinado; 401/302; sem segredos nas respostas)
- [x] T015 `tasks.md` fechada

---

## Notes

- Sessões/tokens **não** persistidos; segredos por ambiente lidos por requisição
- Autoria das escritas mantém `OPERATOR_NAME` (Q3=A)
- Sem senha/segredo/token → acesso bloqueado (FR-007)
