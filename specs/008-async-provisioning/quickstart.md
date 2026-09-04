# Quickstart: Execução Assíncrona (validação)

**Branch**: `008-async-provisioning` | **Date**: 2026-09-04 | **Spec**: [spec.md](spec.md)

## Setup
```powershell
$env:AUTOMATIC1_ASYNC = "1"   # padrão; "0" = síncrono
.\scripts\setup-dev.ps1; .\scripts\test.ps1; .\scripts\run.ps1
```

## Cenários

### C1 — Disparo imediato (US1)
1. Em um setup com máquina ativa, "⚡ Provisionar" → confirmar.
- **Esperado**: resposta imediata; `Execution` em `em_andamento`; página do setup **atualiza automaticamente** até o worker concluir (`sucesso`/`erro` + log).

### C2 — Acompanhamento (US2)
1. Durante uma execução (runner fake/demo), abrir o detalhe.
- **Esperado**: auto-refresh; ao concluir, estado terminal. Via API: `GET /api/execucoes/{id}` (token de leitura) retorna status + log sanitizado; `404` se inexistente.

### C3 — Concorrência/robustez (US3)
1. Disparo duplo do mesmo par enquanto há `em_andamento` → bloqueado.
2. Reinício com execução `em_andamento` → recuperada como interrompida (`recuperar_orfas`).

## Critérios automatizados
| Teste | Cobre |
|-------|-------|
| `tests/test_async_provisioning.py` | C1–C3 |
| demais suítes | regressão 001–007 (ASYNC=0 determinístico) |
