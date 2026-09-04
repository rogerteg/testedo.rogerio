# Quickstart: API de Escrita (validação)

**Branch**: `007-write-api` | **Date**: 2026-09-04 | **Spec**: [spec.md](spec.md)

Guia de validação. Contrato: [contracts/api.md](contracts/api.md).

## Pré-requisitos (ambiente)
```powershell
$env:AUTOMATIC1_WRITE_API_TOKEN = "..."
```

## Cenários

### C1 — Criar setup (US1)
1. `POST /api/setups` com token de escrita e JSON válido → `201` recurso.
2. Nome duplicado → `409`; campo obrigatório ausente/SemVer inválida → `422` com erros por campo; campo com segredo → `422`.

### C2 — Criar máquina (US1)
1. `POST /api/maquinas` válido → `201`. Máquina com credencial (ex.: `token=`) → `422` (rejeitada).

### C3 — Registrar execução (US2)
1. `POST /api/execucoes` (setup + máquina ativa) → `201`; aparece no histórico.
2. Máquina inexistente/inativa ou status inválido → `404`/`400`/`422`; resumo com segredo → `422`.

### C4 — Segurança (US3)
1. Sem token → `401`; token de leitura → `403`; sem `AUTOMATIC1_WRITE_API_TOKEN` → escrita bloqueada.

### C5 — Regressão
1. `pytest` completo verde (leitura `006` + UI inalteradas).

## Critérios de aceite automatizados
| Teste | Cobre |
|-------|-------|
| `tests/test_write_api.py` | C1–C4 |
| demais suítes | regressão |
