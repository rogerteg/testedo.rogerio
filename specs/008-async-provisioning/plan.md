# Implementation Plan: Execução Assíncrona do Provisionamento (008)

**Branch**: `008-async-provisioning` | **Date**: 2026-09-04 | **Spec**: [spec.md](spec.md)

## Summary
Tornar o provisionamento (`004`) **assíncrono**: o disparo retorna imediato (cria `Execution` `em_andamento`), um **worker em processo** conclui (`sucesso`/`erro` + log) e a UI/API permitem **polling**. Execuções órfãs são recuperadas no startup. Sem novas entidades/migração; sem fila externa (v1).

## Technical Context
**Language/Deps**: Python 3.11+; sem dependências novas (ThreadPoolExecutor stdlib). **Storage**: SQLite (inalterado; estado na `Execution`). **Testing**: `tests/test_async_provisioning.py`; `conftest` define `AUTOMATIC1_ASYNC=0` (determinístico p/ regressão `004`). **Project**: web app + worker interno.

## Constitution Check
G1 (test-first) ✅ · G2 (reproduzível/recuperação) ✅ · G3 (sem segredos; log sanitizado) ✅ · G4 (worker simples, sem fila externa) ✅ · G5 (polling/auto-refresh) ✅ · G6 (log; SemVer) ✅ — GATE PASS.

## Decisões (research.md)
D1 fila em threads + recuperação · D2 polling (meta refresh + `GET /api/execucoes/{id}`) · D3 iniciar/concluir + `AUTOMATIC1_ASYNC`.

## Structure
```text
app/provisioner.py  # + iniciar_execucao / concluir_execucao (provisionar = wrapper)
app/worker.py       # NOVO — enfileirar, provisionamento_assincrono, recuperar_orfas
app/routers/{web,api}.py  # rota async + auto-refresh; GET /api/execucoes/{id}
app/main.py         # recuperar_orfas() no startup
tests/test_async_provisioning.py  # NOVO
```
