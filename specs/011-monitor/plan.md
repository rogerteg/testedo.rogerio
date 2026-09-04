# Implementation Plan: Monitoramento/Status dos Serviços (011-monitor)

**Branch**: `011-monitor` | **Date**: 2026-09-04 | **Spec**: [spec.md](spec.md)

## Summary
Adiciona **consulta de status** (somente leitura) da stack de uma máquina alvo via runner
(`docker node ls` + `docker service ls`), com página web e endpoint de API — sem persistir
`Execution`. Saída sempre sanitizada.

## Technical Context
**Language/Deps**: Python 3.11+; sem dependências novas. **Storage**: nenhuma alteração.
**Testing**: `tests/test_monitor.py` (red→green) + regressão. **Project**: FastAPI + SQLModel.

## Constitution Check
G1 (test-first) ✅ · G3 (sem segredos — comando e saída sanitizada) ✅ · G4 (leitura, sem
persistência) ✅ · G6 (comando/saída claros) ✅ — GATE PASS.

## Decisões (research.md)
D1 `docker node ls` + `docker service ls` · D2 runner reusado + `redigir` · D3 web+API sem persistir.

## Structure
```text
app/monitor.py                   # NOVO — montar_comando_status / consultar_status
app/routers/web.py               # GET /maquinas/{id}/status (+ botão no detail)
app/routers/api.py               # GET /api/maquinas/{id}/status
app/templates/maquinas/status.html  # NOVO
tests/test_monitor.py            # NOVO
specs/011-monitor/*              # artefatos SDD
```
