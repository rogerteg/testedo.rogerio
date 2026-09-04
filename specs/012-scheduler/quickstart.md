# Quickstart: Rotina/Agendamento (cron) de Execuções (validação)

**Branch**: `012-scheduler` | **Date**: 2026-09-04 | **Spec**: [spec.md](spec.md)

Guia de validação da feature 012.

## Setup
```powershell
.\scripts\setup-dev.ps1; .\scripts\test.ps1; .\scripts\run.ps1
```

## Cenários

### C1 — Criar agendamento (US1)
1. Nav **Agendamentos** → **+ Novo agendamento** → escolher setup não arquivado + máquina
   ativa + cron (ex.: `0 6 * * *`) → salvar.
- **Esperado**: lista o agendamento ativo com `cron` e "nunca" em último disparo.

### C2 — Validação cron (FR-001)
1. Inserir `99 * * * *` (ou `* * * *` — 4 campos) → salvar.
- **Esperado**: erro por campo acionável; nada persistido.

### C3 — Verificar agora (US3)
1. Criar agendamento `* * * * *` e clicar **▶️ Verificar agora** (ou esperar o disparo).
- **Esperado**: dispara 1× por janela (cria `Execution`; ver histórico do setup); segundo
  clique no mesmo minuto não duplica.

### C4 — Guardas (FR-003)
1. Setup arquivado ou máquina inativa com agendamento ativo → "Verificar agora".
- **Esperado**: bloqueado (sem `Execution`), sem quebrar a rotina.

## Critérios automatizados
| Teste | Cobre |
|-------|-------|
| `tests/test_scheduler.py` | C1–C4 (13 testes) |
| demais suítes | regressão 001–011 |
