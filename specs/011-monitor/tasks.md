---

description: "Task list for Monitoramento/Status dos Serviços (011-monitor)"
---

# Tasks: Monitoramento/Status dos Serviços

**Input**: Design documents from `specs/011-monitor/`

**Status**: ✅ **Concluído** — `tests/test_monitor.py` verde (11 testes) + regressão completa (**151 passed, 4 skip**) + `ruff` limpo.

**Decisões**: Q1=A `docker node ls` + `docker service ls` (leitura) · Q2=A runner reusado + `redigir` · Q3=A web+API sem persistir `Execution`.

## Fase 1 — Módulo monitor (green)

- [x] `app/monitor.py`: `montar_comando_status()` (somente leitura) + `consultar_status()` (saída sanitizada; erro de transporte acionável)

## Fase 2 — Web + API (green)

- [x] `app/routers/web.py`: `GET /maquinas/{id}/status` (guardas: inativa/sem runner)
- [x] `app/routers/api.py`: `GET /api/maquinas/{id}/status` (200/400/404/503)
- [x] `app/templates/maquinas/status.html` + botão no `detail.html`

## Fase 3 — Testes

- [x] `tests/test_monitor.py` (11 testes: comando, consulta fake/erro/redação, web, API)

## Fase 4 — Validação final

- [x] Suíte completa verde (**151 passed, 4 skip**) + `ruff` limpo
- [x] Commit `T056` + push
