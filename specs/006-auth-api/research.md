# Research: Autenticação e API REST (006)

**Branch**: `006-auth-api` | **Date**: 2026-09-03 | **Spec**: [spec.md](spec.md)

Fase 0 do `/speckit-plan`. Resolve Q1–Q3 (A/A/A) e define a abordagem técnica. Formato: *Decision / Rationale / Alternatives considered*.

---

## D1 — Autenticação web (Q1=A)

- **Decision**: **Sessão + senha única** via variável de ambiente. Senha em `AUTOMATIC1_ADMIN_PASSWORD`; comparação segura (`hmac.compare_digest`); **cookie de sessão assinado com expiração** (serializador `itsdangerous` `URLSafeTimedSerializer`, segredo `AUTOMATIC1_SESSION_SECRET`, TTL `AUTOMATIC1_SESSION_TTL` default 8h). Sem gestão de usuários no v1 (nada em banco). Proteção por **middleware**: rotas web protegidas exigem cookie válido (exceto `/login`, `/logout`, `/healthz`, `/static` e `/api/*`); sem cookie → redirect `/login?next=...`.
- **Rationale**: Simples e robusto; segredos por ambiente (constituição IV); `itsdangerous` pequeno e pinado; teste via `TestClient` com cookie.
- **Alternatives considered**: Hash de usuários no banco (gestão de usuários — rejeitado, YAGNI); OAuth/SSO externo (dependência — adiado); sessão em memória do servidor (não escala em multi-processo — rejeitado).

## D2 — API REST somente leitura (Q2=A)

- **Decision**: Endpoints **JSON de leitura** autenticados por **token** (`AUTOMATIC1_API_TOKEN`, cabeçalho `Authorization: Bearer <token>`): `GET /api/setups`, `GET /api/maquinas`, `GET /api/execucoes` (listas). Sem escrita via API no v1. Respostas **sem segredos** (mesmas regras das features `003`/`004`).
- **Rationale**: Integração/monitoração segura (FR-004/FR-005); escopo mínimo e testável.
- **Alternatives considered**: Escrita/operacional via API (maior superfície — adiado; evolui depois).

## D3 — Autoria (Q3=A)

- **Decision**: Mantém-se `OPERATOR_NAME` como autor em todas as escritas das features `001`–`005` (a auth valida a senha única; a auditoria não muda). Sem usuários/identidade própria no v1.
- **Rationale**: Zero mudança no modelo/auditoria; mais simples; identidade granular fica para quando houver gestão de usuários.
- **Alternatives considered**: Usuários com identidade própria (exige CRUD de usuários + migração — rejeitado agora).

## D4 — Segredos/ambiente e bloqueio (FR-007)

- **Decision**: `AUTOMATIC1_ADMIN_PASSWORD`, `AUTOMATIC1_API_TOKEN`, `AUTOMATIC1_SESSION_SECRET` lidas por ambiente **por requisição** (funções em `app/auth.py`) — testável via `monkeypatch`/`os.environ`. Sem senha/token configurados → acesso **bloqueado** com mensagem clara (nunca aceitar vazio).
- **Rationale**: Constituição IV; rotacionável por deploy; teste fácil.
- **Alternatives considered**: Ler no startup/cache (dificulta teste e rotação — rejeitado).

## D5 — Impacto nos testes existentes

- **Decision**: O `conftest.py` passará a **autenticar o client** por padrão (configura senha no ambiente e faz `POST /login` para obter o cookie; `TestClient` mantém cookies). Testes novos de auth/API cobrem os cenários 401/redirect/403. Suíte `001`–`005` permanece verde (agora autenticada).
- **Rationale**: Adicionar auth **quebra** os testes atuais que acessam sem sessão — autenticar o client default preserva a regressão e adiciona cobertura real.
- **Alternatives considered**: Deixar rotas abertas sem senha configurada (viola FR-007 — rejeitado).

## D6 — Estrutura

- **Decision**: `app/auth.py` (helpers de sessão/token/senha); `app/routers/api.py` (endpoints de leitura com dependência de token); middleware de sessão em `app/main.py`; templates `login.html`; rotas `/login`/`/logout`. Nova dependência **`itsdangerous`** (pinada).
- **Rationale**: Separação clara; API isolada; middleware cobre todas as rotas web (inclui futuras).
- **Alternatives considered**: Proteção rota a rota via dependência (repetitivo — middleware é mais coeso).
