# Research: API de Escrita (007)

**Branch**: `007-write-api` | **Date**: 2026-09-04 | **Spec**: [spec.md](spec.md)

Fase 0 do `/speckit-plan`. Resolve Q1–Q3 (A/A/A). Formato: *Decision / Rationale / Alternatives*.

## D1 — Escopo (Q1=A)
- **Decision**: Escritas v1 = **criar setup**, **criar máquina** e **registrar execução** (JSON). Editar/arquivar/desativar/provisionar via API ficam para depois.
- **Rationale**: Alimenta o catálogo/histórico por integração com escopo contido e seguro.
- **Alternatives**: escrita completa (inclui provisionar) — maior risco; editar/arquivar — maior superfície (adiados).

## D2 — Token de escrita (Q2=A)
- **Decision**: Novo `AUTOMATIC1_WRITE_API_TOKEN` (Bearer), separado do de leitura. Regras: ausente/outro → `401`; token de leitura (`AUTOMATIC1_API_TOKEN`) em escrita → `403`.
- **Rationale**: least-privilege; segredos por ambiente (constituição IV).
- **Alternatives**: token único full-access (rejeitado).

## D3 — Validação/erros (Q3=A)
- **Decision**: Reutilizar `validar_campos`/`validar_maquina`/`validar_execucao` + unicidade/anti-segredo. Erros por campo `{"campo": "mensagem"}`: `422` validação, `409` duplicado, `404` inexistente, `201` criado (recurso JSON). Autor = `OPERATOR_NAME`.
- **Rationale**: Consistente com a UI; mensagens acionáveis PT-BR; sem segredos.
- **Alternatives**: erro genérico (menos acionável).

## D4 — Estrutura
- **Decision**: Endpoints novos em `app/routers/api.py` (mesmo router, rotas POST) com dependência `exigir_token_escrita`; reutiliza serializadores `*_para_json`. Body JSON via `dict` + normalização de strings (mesma da UI).
- **Rationale**: Reuso máximo; sem nova camada.
