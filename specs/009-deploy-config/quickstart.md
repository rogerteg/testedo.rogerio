# Quickstart: Config de Deploy por Setup (validação)

**Branch**: `009-deploy-config` | **Date**: 2026-09-04 | **Spec**: [spec.md](spec.md)

Guia de validação da feature 009.

## Setup
```powershell
.\scripts\setup-dev.ps1; .\scripts\test.ps1; .\scripts\run.ps1
```

## Cenários

### C1 — Configurar deploy de um setup (US1)
1. Novo setup → preencher `Domínio` (ex.: `n8n.exemplo.com`) e `Variáveis de deploy`
   (linhas `CHAVE=valor`, ex.: `AUTOMATIC1_N8N_VERSION=latest`).
- **Esperado**: salva; exibidos no detalhe; nenhum segredo aceito (erro por campo).

### C2 — Rejeição de segredo (US1/FR-013)
1. Inserir `AUTOMATIC1_SENHA=123456` em variáveis (ou `token.x` no domínio) e salvar.
- **Esperado**: erro por campo, dados preservados, nada persistido.

### C3 — Injeção no provisionamento (US2)
1. Setup com config + máquina ativa + runner fake/SSH → "⚡ Provisionar".
- **Esperado**: comando remoto contém `export AUTOMATIC1_DOMAIN='...'` e
  `export CHAVE='valor'` antes do download do asset (ver teste
  `test_montar_comando_exporta_config`).

### C4 — API (US3)
1. `POST /api/setups` com `dominio`/`variaveis_deploy` + token de escrita → 201.
2. Com segredo → 422. Leitura `GET /api/setups` → campos presentes.

## Critérios automatizados
| Teste | Cobre |
|-------|-------|
| `tests/test_deploy_config.py` | C1–C4 (13 testes) |
| demais suítes | regressão 001–008 |
