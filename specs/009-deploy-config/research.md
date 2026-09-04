# Research: Config de Deploy por Setup (009-deploy-config)

**Branch**: `009-deploy-config` | **Date**: 2026-09-04 | **Spec**: [spec.md](spec.md)

Resolve Q1–Q3 (A/A/A). Formato: *Decision / Rationale / Alternatives*.

## D1 — Quais parâmetros por setup? (Q1=A)
- **Decision**: `dominio` (texto opcional) + `variaveis_deploy` (linhas `CHAVE=valor`,
  uma por linha, **sem segredos**).
- **Rationale**: Cobre o caso real (domínio/subdomínio p/ Traefik + env vars simples);
  simples de persistir/validar; sem estrutura aninhada (YAGNI).
- **Alternatives**: JSON estruturado por setup (complexo p/ form); segredos por setup
  (rejeitado — constituição IV).

## D2 — Como a config chega ao provisionamento? (Q2=A)
- **Decision**: `montar_comando` **prefixa** `export CHAVE='valor'` no comando remoto
  (e `AUTOMATIC1_DOMAIN` quando `dominio` presente), antes de baixar/rodar o asset.
- **Rationale**: O script instalador lê env vars; idempotente; sem tocar no runner/SSH.
- **Alternatives**: flags de CLI no asset (acoplado a cada script — rejeitado).

## D3 — Persistência/migração (Q3=A)
- **Decision**: Colunas aditivas `dominio VARCHAR(255)` e `variaveis_deploy TEXT` na
  tabela `environment_setup`, via `_migrar_schema` (PRAGMA + ALTER, idempotente).
- **Rationale**: Sem quebra de schema; mesmo padrão das features 002/004.
- **Alternatives**: nova tabela filha (mais normalizado, porém mais partes móveis —
  rejeitado no v1).
