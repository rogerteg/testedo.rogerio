# Implementation Plan: Backup/Exportação do Catálogo (010-backup)

**Branch**: `010-backup` | **Date**: 2026-09-04 | **Spec**: [spec.md](spec.md)

## Summary
Adiciona **exportação/importação** do catálogo (setups+máquinas+execuções) em **JSON**,
aditiva e com validação anti-segredo. Snapshot com meta (formato/versão/data/autor) e
execuções com nomes desnormalizados p/ restauração em ids novos.

## Technical Context
**Language/Deps**: Python 3.11+; stdlib `json`/`datetime`. **Storage**: leitura/escrita
no SQLite existente; **sem migração**. **Testing**: `tests/test_backup.py` (red→green) +
regressão. **Project**: FastAPI + SQLModel (web; export/import protegidos por sessão).

## Constitution Check
G1 (test-first) ✅ · G3 (anti-segredo reaplicado no import — IV) ✅ · G4 (JSON simples,
sem dep) ✅ · G5 (relatório claro) ✅ — GATE PASS.

## Decisões (research.md)
D1 JSON com meta + coleções (execuções com nomes) · D2 import aditivo · D3 validação reusada.

## Structure
```text
app/backup.py                   # NOVO — serializar/montar_snapshot/importar_snapshot
app/routers/web.py              # GET /backup/exportar, GET /backup, POST /backup/importar
app/templates/backup.html       # NOVO (exportar + importar)
app/templates/base.html         # nav + item "Backup"
tests/test_backup.py            # NOVO
specs/010-backup/*              # artefatos SDD
```
