---

description: "Feature spec for Rotina/Agendamento (cron) de Execuções (012-scheduler)"
---

# Spec: Rotina/Agendamento (cron) de Execuções

**Feature**: `012-scheduler` | **Branch**: `012-scheduler`
**Status**: Draft | **Date**: 2026-09-04

## Input / Justificativa

O provisionamento hoje é disparado manualmente (004) e roda assíncrono (008). Para
**revalidação/rotina**, o operador quer **agendar** provisionamentos recorrentes (cron)
por setup × máquina, além do disparo manual. Esta feature adiciona **agendamentos**
(rotina interna) com disparo pelo worker existente.

## User Stories

### US1 — Agendar execução (admin web)
Como administrador, quero **criar/gerenciar agendamentos** (cron) de um setup numa
máquina, para revalidar/atualizar de forma recorrente sem ação manual.

- Novo modelo `Agendamento` (`setup_id`, `target_host_id`, `cron`, `ativo`).
- UI em `/agendamentos`: listar, criar, ativar/desativar, excluir.

### US2 — Executar agendamentos vencidos (rotina interna)
Como administrador, quero que os agendamentos **vencidos** disparem execuções
assíncronas automaticamente (reuso do worker 008), sem bloquear a UI.

- `app/agendador.py`: `vencidos_em(session, agora)` + `executar_vencidos(session, autor)`.
- Disparo: criar `Execution` `em_andamento` (mesmas guardas de 004) + `enfileirar` (008).

### US3 — Verificar agora (admin web)
Como administrador, quero um botão "**Verificar agora**" p/ executar vencidos sob
demanda (sem esperar o tick) e ver o relatório.

## Functional Requirements

- **FR-001**: Expressão cron DEVE ser **5 campos** (`minuto hora dia mês dia-semana`)
  com suporte a `*`, `*/passo` e listas `a,b`; validação com mensagem acionável.
- **FR-002**: Um agendamento ativo com expressão vencida num dado instante DEVE disparar
  no máximo 1 execução por janela (evita duplicação no mesmo minuto/instante).
- **FR-003**: Guardas de provisionamento (setup arquivado/máquina inativa/em andamento)
  DEVEM ser reusadas (004) — agendamento não ignora bloqueios.
- **FR-004**: Disparo em background reusa o worker (008): cria `em_andamento` e enfileira.
- **FR-005**: Sem segredos (constituição IV); autor = `OPERATOR_NAME`.

## Non-Functional / Constraints

- Cron parser **caseiro** (sem dependência nova; supply-chain review evita lib).
- Sem migração destrutiva (nova tabela via `create_all`).
- Test-first; regressão completa verde. Conftest segue com `ASYNC=0`; testes de rotina
  usam o módulo puro + monkeypatch de `enfileirar`.

## Out of Scope

- Cron avançado (aniversários, timezone/`TZ`) — v1 usa hora local do servidor.
- Painel de histórico de disparos dedicado (histórico fica em `Execution`).

## Acceptance Criteria (quickstart/checklist)

- [ ] Validação cron (5 campos, `*`, passo, listas) com mensagens claras.
- [ ] `vencidos_em`/`executar_vencidos` corretos (dispara 1×/janela; respeita guardas).
- [ ] CRUD web de agendamentos + botão "Verificar agora".
- [ ] Suíte completa verde.
