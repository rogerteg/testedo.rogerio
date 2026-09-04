# Implementation Plan: Rotina/Agendamento (cron) de Execuções (012-scheduler)

**Branch**: `012-scheduler` | **Date**: 2026-09-04 | **Spec**: [spec.md](spec.md)

## Summary
Adiciona **agendamentos cron** (setup × máquina) que disparam execuções assíncronas
recorrentes reusando o worker (008). Novo modelo `Agendamento` (sem migração destrutiva),
parser cron caseiro (5 campos), `app/agendador.py` (vencidos/executar), CRUD web e botão
"Verificar agora".

## Technical Context
**Language/Deps**: Python 3.11+; sem dependências novas (parser caseiro). **Storage**: nova
tabela `agendamento` via `create_all` (SQLModel). **Testing**: `tests/test_scheduler.py`
(red→green) + regressão; conftest `ASYNC=0`; testes de disparo com monkeypatch `enfileirar`.
**Project**: FastAPI + SQLModel.

## Constitution Check
G1 (test-first) ✅ · G3 (sem segredos) ✅ · G4 (parser caseiro, sem dep) ✅ ·
G5 (relatório "Verificar agora") ✅ — GATE PASS.

## Decisões (research.md)
D1 cron 5 campos caseiro · D2 1×/janela por minuto · D3 iniciar_execucao + enfileirar ·
D4 tabela nova + CRUD web.

## Data Model Delta
`Agendamento` (tabela `agendamento`): `id`, `setup_id` FK, `target_host_id` FK,
`cron` (str 100), `ativo` (bool, default True), `ultimo_disparo` (datetime nullable),
`created_at/updated_at`, `created_by/updated_by`.

## Structure
```text
app/models.py        # + Agendamento
app/agendador.py     # NOVO — validar_cron/expressao_casa/vencidos_em/executar_vencidos
app/routers/web.py   # /agendamentos CRUD + "Verificar agora"
app/templates/agendamentos/{list,form}.html  # NOVOS
app/templates/base.html  # nav
tests/test_scheduler.py  # NOVO
specs/012-scheduler/*    # artefatos SDD
```
