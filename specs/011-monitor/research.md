# Research: Monitoramento/Status dos Serviços (011-monitor)

**Branch**: `011-monitor` | **Date**: 2026-09-04 | **Spec**: [spec.md](spec.md)

Resolve Q1–Q3 (A/A/A). Formato: *Decision / Rationale / Alternatives*.

## D1 — O que o status consulta? (Q1=A)
- **Decision**: Comando **somente leitura** no host: estado do nó swarm (`docker node ls`) +
  `docker service ls` (nome/modo/réplicas/imagem) — suficiente p/ saúde pós-instalação.
- **Rationale**: Cobra o caso real sem inventar métricas; legível e determinístico.
- **Alternatives**: coletar CPU/RAM por serviço (complexo e caro — v2); ping TCP/HTTP por app
  (depende de rota/dominio por serviço — exige feature 009 por app, adiado).

## D2 — Como executar? (Q2=A)
- **Decision**: Mesmo runner do provisionador (`criar_runner()`); `FakeRunner` nos testes.
  Reuso de `redigir` p/ sanitizar a saída.
- **Rationale**: Sem nova infra; consistente com 004/008.
- **Alternatives**: agente instalado no host (over-engineering no v1).

## D3 — Web + API, sem persistir (Q3=A)
- **Decision**: Página web `/maquinas/{id}/status` (botão no detalhe) + API de leitura
  `GET /api/maquinas/{id}/status`. **Não** cria `Execution` — consulta pontual de leitura.
- **Rationale**: Entrega valor imediato sem poluir histórico/schema (YAGNI).
- **Alternatives**: gravar status como `Execution` (polui semântica — rejeitado no v1).
