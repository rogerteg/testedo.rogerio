# Quickstart: Monitoramento/Status dos Serviços (validação)

**Branch**: `011-monitor` | **Date**: 2026-09-04 | **Spec**: [spec.md](spec.md)

Guia de validação da feature 011.

## Setup
```powershell
.\scripts\setup-dev.ps1; .\scripts\test.ps1; .\scripts\run.ps1
```

## Cenários

### C1 — Status web (US1)
1. Máquina **ativa** com runner SSH configurado (ou `AUTOMATIC1_RUNNER=fake`) →
   detalhe da máquina → **🩺 Verificar status**.
- **Esperado**: página com saída (`docker node ls` + `docker service ls`) e badge de sucesso/erro.

### C2 — Guardas (US1)
1. Máquina **inativa** → mensagem "inativa" (sem execução).
2. Sem runner (`AUTOMATIC1_SSH_KEY` ausente e `RUNNER != fake`) → orientação de credencial.

### C3 — API (US2)
1. `GET /api/maquinas/{id}/status` com token de leitura → `{"status": "sucesso"|"erro", "saida": ..., "exit_code": ...}`.
2. Sem token → 401; inexistente → 404; inativa → 400; sem runner → 503.

## Critérios automatizados
| Teste | Cobre |
|-------|-------|
| `tests/test_monitor.py` | C1–C3 (11 testes) |
| demais suítes | regressão 001–010 |
