---

description: "Task list for Provisionador Real (004-provisioner)"
---

# Tasks: Provisionador Real

**Input**: Design documents from `specs/004-provisioner/`

**Status**: ✅ **Concluído** — suíte `tests/test_provisioner.py` verde (12 testes, `FakeRunner`, sem rede) + regressão completa (**75 passed**) + `ruff` limpo.

## Format: `[ID] [P?] [Story] Description`

## Path Conventions

- **Single project (FastAPI monólito)**: `app/`, `tests/`, `scripts/` na raiz.

---

## Phase 1: Foundational (Blocking)

- [x] T001 [P] [FOUND] `Execution` + colunas aditivas nullable `log`/`exit_code`/`started_at`/`finished_at` em `app/models.py`
- [x] T002 [FOUND] Migração aditiva idempotente (PRAGMA+ALTER) generalizada em `app/database.py` (execution)
- [x] T003 [P] [FOUND] `AUTOMATIC1_SSH_*` em `app/config.py`
- [x] T004 [FOUND] `paramiko` adicionado/pinado em `pyproject.toml` (`uv sync`)
- [x] T005 [P] [FOUND] `app/runners.py`: `RunResult`, `FakeRunner`, `SSHRunner`, `criar_runner()`

**Checkpoint**: Fundação pronta.

---

## Phase 2: Testes — Vermelho (Red) ⚠️

- [x] T006 [P] [US1/US3] Sucesso e falha (Execution real com status/log/exit/horários)
- [x] T007 [P] [US3] Guardas (arquivado, inativa, origem não executável, em andamento, credencial ausente)
- [x] T008 [P] [US3] Integridade/redação (`montar_comando` sha256; `redigir`)
- [x] T009 [P] [US2] Reexecução preserva histórico + HTTP (rota provisionar)

**Checkpoint**: Vermelho confirmado.

---

## Phase 3: User Story 1/3 - Engine de provisionamento (P1) 🎯

- [x] T010 [P] [US1/US3] `app/provisioner.py`: `ProvisionamentoError`, `montar_comando`, `redigir`, `avaliar`, `provisionar`
- [x] T011 [US1/US3] Rotas `GET/POST /setups/{setup_id}/provisionar` em `app/routers/web.py`
- [x] T012 [P] [US1] Template `app/templates/setups/provisionar.html`

**Checkpoint**: Engine + rota + UI funcionais.

---

## Phase 4: User Story 2 - Acompanhar/reexecutar (P2)

- [x] T013 [US2] `setups/detail.html` e `maquinas/detail.html`: colunas `exit_code`/log sanitizado + botão "⚡ Provisionar"
- [x] T014 [US2] Mensagem `sucesso=execucao_provisionada` no detalhe + reexecução preserva histórico

**Checkpoint**: US2 funcional/testada.

---

## Phase 5: Polish & Cross-Cutting

- [x] T015 `quickstart.md` (C1–C6) + `pytest` completo verde (regressão 001–003 = 0)
- [x] T016 [P] Documentação no `README.md` (provisionador real, `AUTOMATIC1_SSH_*`, runner fake, guardas/segurança)
- [x] T017 Revisão de segurança (sem credenciais; log sanitizado; hash; `paramiko` pinado)
- [x] T018 `ruff check` limpo + `pytest` final verde (75 passed)

---

## Notes

- Runner: `FakeRunner` (testes) / `SSHRunner` (produção, `paramiko`); `criar_runner()` → `None` sem chave → guarda
- `origem_asset` precisa ser `.sh` para executar; senão bloqueio acionável
- Hash presente → sha256 no host antes de executar; ausente → aviso
- Log sempre sanitizado (FR-005); migração aditiva em `execution`
