# Implementation Plan: API de Escrita (007-write-api)

**Branch**: `007-write-api` | **Date**: 2026-09-04 | **Spec**: [spec.md](spec.md)

## Summary

Evoluir a API REST da feature `006` (somente leitura) com **escritas** seguras: criar **setup**, criar **máquina** e **registrar execução** (JSON), autenticadas por **token de escrita** (`AUTOMATIC1_WRITE_API_TOKEN`), reutilizando as validações/anti-segredo/unicidade e a auditoria (`OPERATOR_NAME`) da UI. Erros por campo (`422`/`409`/`404`). Sem novas entidades/migração.

## Technical Context

**Language/Version**: Python 3.11+ (mesma stack). **Deps**: nenhuma nova.
**Storage**: SQLite — sem mudança de schema.
**Testing**: `tests/test_write_api.py` (novo) + regressão (read-only `006`, UI `001`–`005`) — test-first.
**Target**: consumidores HTTP externos da API. **Project Type**: Web app + API REST.
**Constraints**: token de escrita por ambiente (constituição IV); leitura em escrita → `403`, ausente → `401`; sem token → bloqueio; autor `OPERATOR_NAME`; sem segredos em respostas/erros.

## Constitution Check

- G1 Test-First: testes antes do core. ✅ · G2 Reproducível: sem alteração de bootstrap. ✅
- G3 Security (IV): token por ambiente; rejeição de credencial; sem segredos. ✅
- G4 Simplicity/YAGNI: só criações + registrar execução; sem novas camadas. ✅
- G5 UX: erros por campo PT-BR. ✅ · G6 Observabilidade: log de escritas; SemVer. ✅
**Resultado**: GATE PASS.

## Key Design Decisions (research.md)
1. Escopo v1 = criar setup/máquina + registrar execução (Q1=A) — D1.
2. Token de escrita separado (Q2=A) — D2.
3. Validações/erros reutilizados; autor `OPERATOR_NAME` (Q3=A) — D3.
4. Endpoints POST em `app/routers/api.py` com `exigir_token_escrita` — D4.

## Structure
```text
app/
├── auth.py                  # + token_escrita_valido (AUTOMATIC1_WRITE_API_TOKEN)
├── routers/api.py           # + POST /api/setups|maquinas|execucoes + exigir_token_escrita
tests/
└── test_write_api.py        # NOVO
```

**Decisão**: mesmo router/api.py (aditivo); reuso dos serializers `*_para_json` e validadores de `schemas`.
