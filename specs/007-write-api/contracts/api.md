# REST API Contract: Escrita (007)

**Branch**: `007-write-api` | **Date**: 2026-09-04 | **Spec**: [spec.md](../spec.md)

Complementa a API de leitura (`006`). Autenticação por **token de escrita** (`AUTOMATIC1_WRITE_API_TOKEN`): `Authorization: Bearer <token>`.

## Autenticação/escopo

| Cenário | Resposta |
|---------|----------|
| Sem token ou token inválido | `401 {"erros": {...}}` |
| Token de **leitura** usado em escrita | `403` |
| Token de escrita válido | executa |

## Endpoints

| Método | Caminho | Body (JSON) | Respostas |
|--------|---------|-------------|-----------|
| POST | `/api/setups` | `nome`*, `plataforma_alvo`*, `origem_asset`* + opcionais (`descricao`, `versao`, `hash`, `licenca`, `status`, `categoria`) | `201` recurso; `422` validação; `409` duplicado |
| POST | `/api/maquinas` | `nome`*, `identificacao`* + opcionais (`plataforma_alvo`, `descricao`) | `201` recurso; `422` validação; `409` duplicado |
| POST | `/api/execucoes` | `setup_id`*, `target_host_id`*, `status`* + `resumo` | `201` recurso; `422` validação; `404` setup/máquina; `400` máquina inativa |

## Erros

`{"erros": {"<campo>": "<mensagem PT-BR>"}}` — sem segredos. `201` retorna o recurso criado (formato dos serializers de `006`).

## Notas
- Validações idênticas à UI (`validar_campos`/`validar_maquina`/`validar_execucao` + anti-segredo/unicidade).
- Autor registrado = `OPERATOR_NAME`.
- Disparar provisionamento/editar/arquivar via API: fora do v1 (escopo futuro).
