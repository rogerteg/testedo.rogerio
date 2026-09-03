# Quickstart: Autenticação e API REST (validação)

**Branch**: `006-auth-api` | **Date**: 2026-09-03 | **Spec**: [spec.md](spec.md)

Guia de validação. Contratos: [contracts/web.md](contracts/web.md) e [contracts/api.md](contracts/api.md).

## Pré-requisitos (ambiente)

```powershell
$env:AUTOMATIC1_ADMIN_PASSWORD = "..."      # senha do operador (login web)
$env:AUTOMATIC1_SESSION_SECRET  = "..."     # segredo p/ assinar o cookie
$env:AUTOMATIC1_API_TOKEN       = "..."     # token da API (leitura)
```

## Setup

```powershell
.\scripts\setup-dev.ps1
.\scripts\test.ps1     # inclui testes de auth/API
.\scripts\run.ps1      # http://127.0.0.1:8000
```

## Cenários

### C1 — Login/logout web (US1)
1. Abrir `/setups` sem sessão → redireciona a `/login?next=/setups`.
2. Login com a senha correta → sessão criada; acessa `/setups`.
3. Senha errada → erro na tela (sem detalhes); logout → volta a exigir login.
4. Sem `AUTOMATIC1_ADMIN_PASSWORD` → login bloqueado com mensagem (FR-007).

### C2 — Proteção das rotas (US1/US3)
1. Sem sessão, tentar `/maquinas`/ações de escrita → redireciona/negado sem efeito.

### C3 — API REST (US2)
1. `GET /api/setups` sem token → `401` JSON.
2. Com `Authorization: Bearer <token>` → `200` JSON (`itens`/`total`); sem segredos.
3. Token errado → `401`; recurso inexistente → `404`.

### C4 — Regressão autenticada (transversal)
1. Suíte `pytest` completa verde (client default autenticado no `conftest`).

## Critérios de aceite automatizados (mapeamento)

| Teste (proposto) | Cobre |
|------------------|-------|
| `tests/test_auth_api.py` | C1–C4 (US1–US3) |
| `tests/` (existentes) | regressão 001–005 (autenticada via conftest) |
