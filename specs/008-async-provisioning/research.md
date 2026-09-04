# Research: Execução Assíncrona do Provisionamento (008)

**Branch**: `008-async-provisioning` | **Date**: 2026-09-04 | **Spec**: [spec.md](spec.md)

Resolve Q1–Q3 (A/A/A). Formato: *Decision / Rationale / Alternatives*.

## D1 — Fila em processo (Q1=A)
- **Decision**: Worker em **threads em processo** (`app/worker.py`, `ThreadPoolExecutor`, `AUTOMATIC1_WORKERS`); sem serviço externo. Execuções órfãs (`em_andamento`) recuperadas no startup (`recuperar_orfas`).
- **Rationale**: Baixo volume interno; simples; recuperação determinística (SC-003).
- **Alternatives**: fila externa Redis/worker (adiado p/ escala).

## D2 — Acompanhamento por polling (Q2=A)
- **Decision**: UI usa auto-refresh (`meta http-equiv=refresh`) quando há `em_andamento`; API ganha `GET /api/execucoes/{id}` (detalhe com log sanitizado) p/ polling.
- **Rationale**: Simples e suficiente; sem SSE/WebSocket (YAGNI).

## D3 — Disparo imediato + estado (Q3=A)
- **Decision**: Refatora `provisioner.py` em `iniciar_execucao` (guardas + cria `em_andamento`) e `concluir_execucao` (runner → terminal); `provisionar` = wrapper síncrono (compat `004`). Rota dispara iniciar e enfileira; `AUTOMATIC1_ASYNC=0` → síncrono (testes/fallback).
- **Rationale**: Mantém regressão `004`; testes determinísticos.
- **Alternatives**: aguardar na request (bloqueia — rejeitado).
