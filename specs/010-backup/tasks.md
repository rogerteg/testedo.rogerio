---

description: "Task list for Backup/Exportação do Catálogo (010-backup)"
---

# Tasks: Backup/Exportação do Catálogo

**Input**: Design documents from `specs/010-backup/`

**Status**: ✅ **Concluído** — `tests/test_backup.py` verde (8 testes) + regressão completa (**140 passed, 4 skip**) + `ruff` limpo.

**Decisões**: Q1=A snapshot JSON com meta + coleções (execuções com nomes) · Q2=A import aditivo/não destrutivo · Q3=A validação/anti-segredo reaplicada no import.

## Fase 1 — Módulo backup (green)

- [x] `app/backup.py`: `montar_snapshot` (meta + setups/maquinas/execuções com `setup_nome`/`maquina_nome`), `importar_snapshot` (aditivo, idempotente p/ execuções), `snapshot_para_json`, `BackupError`
- [x] Validação/anti-segredo reusada (`validar_campos`/`validar_maquina`) no import

## Fase 2 — Rotas web + UI (green)

- [x] `app/routers/web.py`: `GET /backup`, `GET /backup/exportar`, `POST /backup/importar`
- [x] `app/templates/backup.html` + link `Backup` no `base.html`

## Fase 3 — Testes

- [x] `tests/test_backup.py` (8 testes: snapshot, import em vazio, aditivo, segredo, formato inválido, rotas web)

## Fase 4 — Validação final

- [x] Suíte completa verde (**140 passed, 4 skip**) + `ruff` limpo
- [x] Commit `T055` + push
