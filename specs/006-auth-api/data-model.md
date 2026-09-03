# Data Model: Autenticação e API REST (Automatic1)

**Branch**: `006-auth-api` | **Date**: 2026-09-03 | **Spec**: [spec.md](spec.md) | **Research**: [research.md](research.md)

**Sem novas entidades persistidas** (features `001`–`005` intactas). Sessões e tokens **não** ficam no banco:

- **Sessão Web**: cookie assinado com expiração (`itsdangerous` `URLSafeTimedSerializer`), segredo `AUTOMATIC1_SESSION_SECRET`, TTL `AUTOMATIC1_SESSION_TTL` (default 8h). Não persistida.
- **Token de API**: valor em `AUTOMATIC1_API_TOKEN` (ambiente); não persistido; rotação por deploy.
- **Operador**: senha única em `AUTOMATIC1_ADMIN_PASSWORD` (ambiente); autoria continua `OPERATOR_NAME` (Q3=A).

## Configuração nova (ambiente)

| Variável | Default | Descrição |
|----------|---------|-----------|
| `AUTOMATIC1_ADMIN_PASSWORD` | — | Senha do operador (login web) |
| `AUTOMATIC1_SESSION_SECRET` | — | Segredo p/ assinar cookie de sessão |
| `AUTOMATIC1_SESSION_TTL` | `28800` (8h) | Expiração da sessão (segundos) |
| `AUTOMATIC1_API_TOKEN` | — | Token da API REST (somente leitura no v1) |

Sem `ADMIN_PASSWORD`/`API_TOKEN`/`SESSION_SECRET` configurados → acesso bloqueado com mensagem clara (FR-007; nunca aceitar vazio).

## Rotas públicas × protegidas

- **Públicas**: `GET/POST /login`, `GET /logout`, `GET /healthz`, `/static/*`.
- **Protegidas (sessão)**: demais rotas web (`/setups*`, `/maquinas*`).
- **API (token)**: `/api/*` (leitura; `Authorization: Bearer <token>`).

## Notas

- Nenhum segredo em banco/logs/respostas (constituição IV).
- Autoria das escritas mantém `OPERATOR_NAME` (Q3=A).
