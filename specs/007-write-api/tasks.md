---

description: "Task list for API de Escrita (007-write-api)"
---

# Tasks: API de Escrita

**Input**: Design documents from `specs/007-write-api/`

**Status**: ✅ **Concluído** — `tests/test_write_api.py` verde (13 testes) + regressão completa (**112 passed, 4 skip**) + `ruff` limpo.

## Format: `[ID] [P?] [Story] Description`

---

## Phase 1: Foundation

- [x] T001 [FOUND] `token_escrita_valido` em `app/auth.py` (`AUTOMATIC1_WRITE_API_TOKEN`)
- [x] T002 [FOUND] `tests/conftest.py` com env `AUTOMATIC1_WRITE_API_TOKEN`

## Phase 2: Testes — Vermelho ⚠️

- [x] T003 [P] [US1] POST `/api/setups` (201/409/422 validação/422 segredo)
- [x] T004 [P] [US1] POST `/api/maquinas` (201; credencial rejeitada; duplicado)
- [x] T005 [P] [US2] POST `/api/execucoes` (201/404/400/422)
- [x] T006 [P] [US3] Segurança (401 sem token; 403 token de leitura; bloqueio sem env)

## Phase 3: Implementação

- [x] T007 [US1/US2] `app/routers/api.py`: `exigir_token_escrita` + `POST /api/setups|maquinas|execucoes` (JSON; validações/anti-segredo; autor `OPERATOR_NAME`; erros `detail.erros`)

## Phase 4: Polish

- [x] T008 `pytest` completo verde (112) + `ruff` limpo
- [x] T009 [P] `README.md` (token de escrita + endpoints) e `render.yaml` (`AUTOMATIC1_WRITE_API_TOKEN` sync:false)
- [x] T010 `tasks.md` fechada

---

## Notes

- Sem novas entidades/migração; reuso das validações da UI
- Token de escrita por ambiente; leitura→403; ausente→401
- Autor = `OPERATOR_NAME`; sem segredos em respostas/erros
