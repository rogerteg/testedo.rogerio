# Web Interface Contract: Autenticação (006)

**Branch**: `006-auth-api` | **Date**: 2026-09-03 | **Spec**: [spec.md](../spec.md) | **Research**: [research.md](../research.md)

Contrato da camada de autenticação web (server-rendered). Rotas existentes (`001`–`005`) **não mudam de caminho** — passam a exigir sessão.

## Rotas novas

| Método | Caminho | Página | Descrição | Origem |
|--------|---------|--------|-----------|--------|
| GET | `/login` | login | Formulário de login (público) | US1 |
| POST | `/login` | — (redirect) | Valida a senha do ambiente (`AUTOMATIC1_ADMIN_PASSWORD`); sucesso → sessão (`Set-Cookie`) e `303` para `next` ou `/setups`; falha → re-render com erro, sem expor detalhes | US1 |
| GET | `/logout` | — (redirect) | Invalida a sessão (cookie expirado) e `303 → /login` | US1 |

## Proteção (middleware)

- **Públicas**: `/login`, `/logout`, `/healthz`, `/static/*`, `/api/*`.
- **Protegidas**: demais (`/setups*`, `/maquinas*`) — sem sessão válida → `302 /login?next=<origem>`.
- Cookie: `automatic1_session` (assinado, `HttpOnly`, `SameSite=Lax`).

## Estados/feedback

- Sem senha configurada (`AUTOMATIC1_ADMIN_PASSWORD`) → login bloqueado com mensagem clara (FR-007).
- Sessão expirada → redireciona ao login com `next` preservado.
- Logout sempre disponível no topo (base) quando autenticado.

## Validação/auditoria

- Tentativa inválida registrada em log (sem detalhes sensíveis) — FR-008.
- Autoria das escritas mantém `OPERATOR_NAME` (Q3=A).
