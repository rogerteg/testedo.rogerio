---

description: "Task list for Rotina/Agendamento (cron) de Execuções (012-scheduler)"
---

# Tasks: Rotina/Agendamento (cron) de Execuções

**Input**: Design documents from `specs/012-scheduler/`

**Status**: ✅ **Concluído** — `tests/test_scheduler.py` verde (13 testes) + regressão completa (**164 passed, 4 skip**) + `ruff` limpo.

**Decisões**: Q1=A cron 5 campos caseiro · Q2=A 1×/janela por minuto · Q3=A iniciar_execucao + worker 008 · Q4=A tabela nova + CRUD web + rotina interna em thread (`AUTOMATIC1_SCHEDULER`).

## Fase 1 — Modelo + agendador (green)

- [x] `app/models.py`: `Agendamento` (tabela nova via `create_all`; sem migração destrutiva)
- [x] `app/agendador.py`: `validar_cron`, `expressao_casa`, `vencidos_em` (1×/janela, tz normalizada), `executar_vencidos` (guardas 004 + worker 008), `iniciar_rotina`/`_loop_rotina` (thread daemon)

## Fase 2 — Web + UI + rotina (green)

- [x] `app/routers/web.py`: CRUD `/agendamentos` (criar/listar/desativar/ativar/excluir) + `POST /agendamentos/verificar`
- [x] `app/templates/agendamentos/{list,form}.html` + nav "Agendamentos"
- [x] `app/main.py`: `iniciar_rotina()` no lifespan quando `AUTOMATIC1_SCHEDULER != "0"`
- [x] `tests/conftest.py`: `AUTOMATIC1_SCHEDULER=0` (testes sem thread)

## Fase 3 — Testes

- [x] `tests/test_scheduler.py` (13 testes: validação cron, expressao_casa, vencidos, executar com guardas, CRUD web + verificar agora)

## Fase 4 — Validação final

- [x] Suíte completa verde (**164 passed, 4 skip**) + `ruff` limpo
- [x] Commit `T057` + push
