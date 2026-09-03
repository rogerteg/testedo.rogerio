# REST API Contract: Leitura (006)

**Branch**: `006-auth-api` | **Date**: 2026-09-03 | **Spec**: [spec.md](../spec.md)

API **somente leitura** no v1 (Q2=A), autenticada por token (`AUTOMATIC1_API_TOKEN`) via cabeçalho.

## Autenticação

`Authorization: Bearer <token>` — comparação segura; ausente/inválido → `401 {"erro": "..."}`. Sem segredos nas respostas.

## Endpoints

| Método | Caminho | Descrição |
|--------|---------|-----------|
| GET | `/api/setups` | Lista setups (ativos; exclui `arquivado`); opcional `?q=` e `?categoria=` |
| GET | `/api/maquinas` | Lista máquinas alvo (sem credenciais — nunca há) |
| GET | `/api/execucoes` | Lista execuções (opcional `?setup_id=`/`?maquina_id=`; mais recentes primeiro) |

## Resposta

`200` com JSON `{"itens": [...], "total": N}`. Campos em formato estável (mesmos das entidades, PT). Erros: `401` não autenticado; `403/404` recurso fora do escopo (não usado no v1 read-only — reservado); `500` inesperado com `{"erro": "..."}` genérico.

## Exemplo

```http
GET /api/setups HTTP/1.1
Authorization: Bearer <token>
```

## Escopo futuro

Escritas (criar/editar/arquivar, registrar execução, provisionar) via API **não** fazem parte do v1 — evoluem depois (D2).
