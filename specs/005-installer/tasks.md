---

description: "Task list for Instalador Próprio do Automatic1 (005-installer)"
---

# Tasks: Instalador Próprio do Automatic1

**Input**: Design documents from `specs/005-installer/`

**Status**: ✅ **Concluído (framework + app de referência)** — `tests/test_installer.py` verde (12 passed; 4 `bash -n` skipped por bash WSL inutilizável) + regressão completa (**87 passed**) + `ruff` limpo. **Validação E2E real em host Debian = manual** (registrado; não executável neste ambiente).

## Format: `[ID] [P?] [Story] Description`

## Path Conventions

- Instalador: `installer/`; testes em `tests/`.

---

## Phase 1: Framework do instalador (Foundation)

- [x] T001 [P] [FOUND] `installer/lib/common.sh` (log/die/require_root/config env/idempotência por marcadores/manifesto)
- [x] T002 [FOUND] `installer/bootstrap.sh` (Docker + Swarm idempotente; `--check`/dry-run; exit codes)
- [x] T003 [P] [FOUND] `installer/install.sh` (`--help`/`--version`/`--check`/execução; bootstrap + apps de `AUTOMATIC1_APPS`)
- [x] T004 [P] [FOUND] `installer/config.example.env` + `installer/apps/README.md` (padrão de novas ferramentas)
- [x] T005 [P] [US2] `installer/apps/n8n.sh` (app de referência idempotente)

**Checkpoint**: Framework pronto.

---

## Phase 2: Testes

- [x] T006 [P] Testes estruturais `tests/test_installer.py` (arquivos/shebang/anti-segredo/consistência env)
- [x] T007 [FOUND] `bash -n` com skip quando o bash é inutilizável (WSL stub neste ambiente)

**Checkpoint**: Vermelho confirmado antes da criação dos arquivos.

---

## Phase 3: Instalador (P1) 🎯

- [x] T008 [US1] `--check`/dry-run com exit codes e pré-requisitos (root/Debian)
- [x] T009 [US2/US3] Idempotência por marcadores + manifesto (stdout/arquivo)

**Checkpoint**: Instalador funcional (validação estrutural).

---

## Phase 4: Polish & Cross-Cutting

- [x] T010 `pytest` completo verde (87 passed, regressão 001–004 = 0) + `ruff` limpo
- [x] T011 [P] Documentação no `README.md` (seção instalador + limitação E2E)
- [x] T012 Revisão de segurança (sem segredos; exit codes; exceção runtime bash registrada)
- [x] T013 `tasks.md` fechada

---

## Notes

- E2E real (bootstrap/apps num Debian) é **manual** (host de teste) — `quickstart.md` Parte B
- Ligação catálogo→`origem_asset` e demais ferramentas: **incremental**, quando os scripts estiverem hospedados
- Headless (config/env); sem segredos embutidos; exceção runtime PowerShell→bash/Debian registrada
