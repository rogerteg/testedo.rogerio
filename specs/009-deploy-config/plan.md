# Implementation Plan: Config de Deploy por Setup (009-deploy-config)

**Branch**: `009-deploy-config` | **Date**: 2026-09-04 | **Spec**: [spec.md](spec.md)

## Summary
Adiciona **configuração de deploy por setup**: `dominio` (opcional) e `variaveis_deploy`
(linhas `CHAVE=valor`, sem segredos). A config é validada (web + API 007), persistida por
migração aditiva e **exportada no provisionamento** (004/008) antes de rodar o asset —
habilitando roteamento Traefik/parametrização real.

## Technical Context
**Language/Deps**: Python 3.11+; sem dependências novas. **Storage**: SQLite — migração
aditiva idempotente em `environment_setup`. **Testing**: suíte nova `test_deploy_config.py`
(red→green) + regressão completa. **Project**: FastAPI + SQLModel monólito (web + API).

## Constitution Check
G1 (test-first) ✅ · G3 (sem segredos nos novos campos — FR-013/IV) ✅ · G4 (2 campos simples,
YAGNI) ✅ · G6 (export no provisionamento mantém log redigido) ✅ — GATE PASS.

## Decisões (research.md)
D1 `dominio` + `variaveis_deploy` (sem segredos) · D2 export no comando remoto ·
D3 colunas aditivas via `_migrar_schema`.

## Data Model Delta (`environment_setup`)
| coluna | tipo | obrig. | observações |
|--------|------|--------|-------------|
| `dominio` | VARCHAR(255) | não | FQDN/subdomínio |
| `variaveis_deploy` | TEXT | não | linhas `CHAVE=valor` (sem segredo) |

## Structure
```text
app/models.py                  # + dominio, variaveis_deploy
app/database.py                # migração aditiva
app/schemas.py                 # validação dos campos (anti-segredo, formato chave)
app/provisioner.py             # montar_comando exporta config (D2)
app/routers/{web,api}.py       # forms + JSON (criar/editar/ver)
app/templates/setups/{form,detail}.html  # UI
tests/test_deploy_config.py    # NOVO
specs/009-deploy-config/*      # artefatos SDD
```
