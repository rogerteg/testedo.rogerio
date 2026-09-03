---

description: "Task list for Máquinas Alvo e Execuções (003-machines-runs)"
---

# Tasks: Máquinas Alvo e Execuções

**Input**: Design documents from `specs/003-machines-runs/`

**Status**: ✅ **Concluído** — suíte `tests/test_maquinas_execucoes.py` verde (18 testes) + regressão completa (**63 passed**) + `ruff` limpo.

## Format: `[ID] [P?] [Story] Description`

## Path Conventions

- **Single project (FastAPI monólito)**: `app/`, `tests/`, `scripts/` na raiz.

---

## Phase 1: Foundational (Blocking)

- [x] T001 [P] [FOUND] `TargetHost` e `Execution` em `app/models.py` (FKs; `environment_setup` inalterado)
- [x] T002 [P] [FOUND] Constantes/validação em `app/schemas.py` (`validar_maquina`, `validar_execucao`, status/labels PT-BR)
- [x] T003 [FOUND] `init_db()` cria tabelas novas via `create_all` (idempotente; sem ALTER)

**Checkpoint**: Fundação pronta.

---

## Phase 2: Testes — Vermelho (Red) ⚠️

- [x] T004 [P] [US1] `tests/test_maquinas_execucoes.py` — CRUD de máquina + anti-segredo + sem credenciais (C1/C2)
- [x] T005 [P] [US3] Testes de desativação/reativação com/sem aviso (C6)
- [x] T006 [P] [US2] Testes de execução + histórico + validações (C3/C7)
- [x] T007 [P] [US2/US3] Testes de última execução derivada/fallback (C4) e aviso no arquivamento (C5)

**Checkpoint**: Vermelho confirmado antes do core.

---

## Phase 3: User Story 1 - Máquinas alvo (P1) 🎯

- [x] T008 [US1] Rotas de máquina em `app/routers/web.py` (listar/novo/criar/detalhe/editar)
- [x] T009 [P] [US1] Templates `app/templates/maquinas/{list,form,detail}.html`
- [x] T010 [US1] Link "Máquinas" no `app/templates/base.html`

**Checkpoint**: US1 funcional/testada.

---

## Phase 4: User Story 2 - Execuções (P1)

- [x] T011 [US2] Rotas `GET/POST /setups/{setup_id}/executar`
- [x] T012 [P] [US2] Template `app/templates/setups/executar.html`
- [x] T013 [US2] Histórico + última execução derivada no detalhe do setup (`detalhe_setup` + `detail.html`)

**Checkpoint**: US2 funcional/testada.

---

## Phase 5: User Story 3 - Proteção com "utilização ativa" (P2)

- [x] T014 [US3] Desativar/Reativar máquina (confirmação + aviso) + `maquinas/desativar.html`
- [x] T015 [US3] Aviso com contagem no arquivamento (`arquivar.html`)

**Checkpoint**: US3 funcional/testada.

---

## Phase 6: Polish & Cross-Cutting

- [x] T016 `quickstart.md` (C1–C7) + `pytest` completo verde (regressão 001/002 = 0)
- [x] T017 [P] Documentação no `README.md` (máquinas, execuções, sem credenciais, aviso)
- [x] T018 Revisão de segurança (sem credenciais; anti-segredo; auditoria)
- [x] T019 `ruff check` limpo + `pytest` final verde (63 passed)

---

## Notes

- Execução = **registro/estado** (nada executado); provisionamento real = Etapa 3
- Máquinas **sem credenciais** (apenas metadados)
- `resultado_ultima_execucao` **derivado em leitura** (fallback manual da `001`)
- Tabelas novas via `create_all`; `environment_setup` inalterado
