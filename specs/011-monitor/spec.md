---

description: "Feature spec for Monitoramento/Status dos Serviços (011-monitor)"
---

# Spec: Monitoramento/Status dos Serviços

**Feature**: `011-monitor` | **Branch**: `011-monitor`
**Status**: Draft | **Date**: 2026-09-04

## Input / Justificativa

Após o provisionamento (004/008), o operador precisa **verificar a saúde** do que foi
instalado no host (Debian + Docker Swarm). Esta feature adiciona uma **consulta de status**
(leitura, via SSH/fake) dos serviços do host, pós-instalação — sem alterar estado.

## User Stories

### US1 — Consultar status de uma máquina (admin web)
Como administrador, quero **ver o status** da stack de uma máquina alvo (nó do swarm +
serviços e réplicas), para conferir a saúde pós-provisionamento.

- Botão "🩺 Verificar status" no detalhe da máquina → `GET /maquinas/{id}/status`.
- Executa comando **somente leitura** via runner; exibe saída sanitizada + exit code.

### US2 — Consultar status via API (consumo externo/monitoração)
Como integrador, quero consultar o status por `GET /api/maquinas/{id}/status`
(token de leitura 006) → `{"status": "sucesso"|"erro", "saida": ..., "exit_code": ...}`.

## Functional Requirements

- **FR-001**: O comando de status DEVE ser **somente leitura** e sem segredos
  (constituição IV): imprime estado do nó e `docker service ls` (nome/modo/réplicas/imagem).
- **FR-002**: A consulta DEVE bloquear máquina **inativa** com mensagem acionável e
  **ausência de runner** (credencial SSH não configurada) com orientação clara.
- **FR-003**: Saída DEVE ser **sanitizada** (`redigir`) antes de exibir (FR-005).
- **FR-004**: A consulta NÃO DEVE criar `Execution` nem alterar estado (YAGNI) — é leitura.

## Non-Functional / Constraints

- Sem nova dependência; sem migração.
- Test-first; regressão completa verde.
- Runner plugável (fake p/ testes — sem rede).

## Out of Scope

- Persistência/histórico de status (observabilidade futura) — v1 é consulta pontual.
- Métricas de recurso detalhadas (CPU/RAM) por serviço (fica p/ v2).

## Acceptance Criteria (quickstart/checklist)

- [ ] Web: detalhe da máquina tem "Verificar status"; página mostra saída + exit code.
- [ ] Máquina inativa/sem runner → mensagens acionáveis.
- [ ] API `GET /api/maquinas/{id}/status` com token de leitura.
- [ ] Saída sempre sanitizada.
- [ ] Suíte completa verde.
