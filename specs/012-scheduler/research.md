# Research: Rotina/Agendamento (cron) de Execuções (012-scheduler)

**Branch**: `012-scheduler` | **Date**: 2026-09-04 | **Spec**: [spec.md](spec.md)

Resolve Q1–Q4 (A/A/A/A). Formato: *Decision / Rationale / Alternatives*.

## D1 — Formato do cron (Q1=A)
- **Decision**: Expressão **5 campos** (`minuto hora dia mês dia-semana`), suporte a
  `*`, `*/passo` e listas `a,b`. Parser **caseiro** em `app/agendador.py`.
- **Rationale**: Suficiente p/ rotinas; evita dependência nova (revisão supply-chain —
  constituição). Mensagens acionáveis na validação.
- **Alternatives**: lib `croniter` (dependência — exigiria revisão; adiado); só intervalo
  fixo (menos expressivo — rejeitado).

## D2 — Janela/duplicação (Q2=A)
- **Decision**: Compara o instante atual por **minuto**; dispara se a expressão casa no
  minuto atual E o `ultimo_disparo` não foi neste minuto (1×/janela).
- **Rationale**: Simples, determinístico, evita rajada por re-tick no mesmo minuto.
- **Alternatives**: fila com locks (over-engineering — worker já serializa por guarda).

## D3 — Disparo (Q3=A)
- **Decision**: `executar_vencidos` chama `iniciar_execucao` (guardas 004 reusadas) e, se
  `provisionamento_assincrono()`, `enfileirar` (008); senão conclui síncrono.
- **Rationale**: Reuso máximo; guardas mantidas; sem novo caminho de execução.
- **Alternatives**: novo runner dedicado (desnecessário).

## D4 — Modelo/UI (Q4=A)
- **Decision**: Nova tabela `agendamento` (via `create_all`, sem ALTER) + CRUD em
  `/agendamentos` + botão "Verificar agora" (chama `executar_vencidos` sob demanda).
- **Rationale**: Simples; sem tocar tabelas existentes.
- **Alternatives**: colunas de cron em `EnvironmentSetup` (acopla setup×máquina×agenda —
  pior).
