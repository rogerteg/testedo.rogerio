# Quickstart: Backup/Exportação do Catálogo (validação)

**Branch**: `010-backup` | **Date**: 2026-09-04 | **Spec**: [spec.md](spec.md)

Guia de validação da feature 010.

## Setup
```powershell
.\scripts\setup-dev.ps1; .\scripts\test.ps1; .\scripts\run.ps1
```

## Cenários

### C1 — Exportar (US1)
1. Logado, nav **Backup** → **⬇ Exportar catálogo**.
- **Esperado**: baixa `automatic1-catalogo-<data>.json` com meta (formato/versão/data/autor)
  e coleções `setups`/`maquinas`/`execucoes` (execuções com `setup_nome`/`maquina_nome`).

### C2 — Importar aditivo (US2)
1. No mesmo banco, subir o snapshot exportado (**⬆ Importar backup**).
- **Esperado**: relatório aditivo (tudo ignorado — nada duplicado); execuções idempotentes.

### C3 — Restaurar em banco vazio
1. Subir o snapshot num banco novo (ex.: remover `data/setups.db` antes de iniciar).
- **Esperado**: cria setups/máquinas/execuções vinculadas; relatório de criados.

### C4 — Rejeição de segredo
1. Editar o JSON para incluir segredo (ex.: `variaveis_deploy` com `SENHA=...`) e importar.
- **Esperado**: item invalidado (anti-segredo FR-013) — nada criado com segredo.

## Critérios automatizados
| Teste | Cobre |
|-------|-------|
| `tests/test_backup.py` | C1–C4 (8 testes) |
| demais suítes | regressão 001–009 |
