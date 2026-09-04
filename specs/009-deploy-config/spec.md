---

description: "Feature spec for Config de Deploy por Setup (009-deploy-config)"
---

# Spec: Config de Deploy por Setup (domínio/vars)

**Feature**: `009-deploy-config` | **Branch**: `009-deploy-config`
**Status**: Draft | **Date**: 2026-09-04

## Input / Justificativa

O catálogo (001–008) registra setups e provisiona scripts `.sh` (004) sem parâmetros
por setup. Na prática (modelo SetupFrancisMno/Traefik), cada app precisa de **configuração
de deploy** (domínio/subdomínio e variáveis) injetada no momento do provisionamento.
Esta feature adiciona **configuração de deploy por setup** — sem segredos (constituição IV).

## User Stories

### US1 — Configurar deploy do setup (admin web + API de escrita)
Como administrador, quero definir por setup um **domínio/subdomínio** e **variáveis
não secretas** (ex.: porta, subdomínio da app), para que o provisionamento seja
parametrizado (ex.: roteamento Traefik).

- Campos opcionais novos em `environment_setup`: `dominio` (texto) e
  `variaveis_deploy` (bloco `CHAVE=valor`, uma por linha).
- **Sem segredos**: valores com sinais de segredo (FR-013) são rejeitados
  (Q1=A — apenas parâmetros não secretos; segredos ficam no cofre/ambiente).

### US2 — Injetar config no provisionamento
Como administrador, quero que o provisionamento (004/008) **exporte** essas variáveis
no host remoto antes de rodar o asset, para que o script instalador leia a config.

- `montar_comando` prefixa `export CHAVE='valor'` (quando há variáveis/domínio).
- Sempre redigido/sem segredos no log (reuso FR-005).

### US3 — Ver/editar config no Admin + API
Como administrador, quero ver a config no detalhe/form do setup e no JSON da API
(`GET/POST /api/setups`) sem segredos.

## Functional Requirements

- **FR-001**: O setup DEVE aceitar `dominio` opcional (FQDN/subdomínio, máx 255).
- **FR-002**: O setup DEVE aceitar `variaveis_deploy` opcional — linhas `CHAVE=valor`,
  sem segredos; chave no formato `[A-Z_][A-Z0-9_]*`; valor sem quebras de linha embutidas.
- **FR-003**: Validação (web + API de escrita 007) DEVE rejeitar segredo nos novos
  campos (mesma política FR-013/anti-segredo).
- **FR-004**: O provisionamento DEVE exportar `dominio` como `AUTOMATIC1_DOMAIN` e as
  variáveis como `export CHAVE='valor'` no comando remoto (quando configuradas).
- **FR-005**: Nenhum segredo DEVE aparecer em banco/UI/log/API (constituição IV).

## Non-Functional / Constraints

- Migração **aditiva** via `_migrar_schema` (ALTER ADD COLUMN) — idempotente.
- Test-first: nova suíte + regressão completa verde.
- Sem nova dependência. Consistente com padrões existentes (form → validar → redirect).

## Out of Scope

- Segredos/credenciais por setup (ficam no cofre/ambiente — FR-004/IV).
- Config por execução individual (apenas por setup).

## Acceptance Criteria (quickstart/checklist)

- [ ] CRUD web cria/edita/exibe `dominio` + `variaveis_deploy` com validação anti-segredo.
- [ ] Provisionamento exporta config no comando (FakeRunner captura `export ...`).
- [ ] API JSON de setups inclui os novos campos (leitura/escrita).
- [ ] Migração aditiva em banco existente idempotente.
- [ ] Suíte completa verde (testes novos + regressão).
