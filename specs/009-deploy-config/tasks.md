---

description: "Task list for Config de Deploy por Setup (009-deploy-config)"
---

# Tasks: Config de Deploy por Setup

**Input**: Design documents from `specs/009-deploy-config/`

**Status**: ✅ **Concluído** — `tests/test_deploy_config.py` verde (13 testes) + regressão completa (**132 passed, 4 skip**) + `ruff` limpo.

**Decisões**: Q1=A `dominio` + `variaveis_deploy` (sem segredos) · Q2=A export no comando remoto · Q3=A colunas aditivas via `_migrar_schema`.

## Fase 1 — Schema/validação (green)

- [x] `tests/test_deploy_config.py` (13 testes: validação, montar_comando, web, API)
- [x] `app/models.py`: `dominio` (VARCHAR 255) e `variaveis_deploy` (TEXT)
- [x] `app/database.py`: migração aditiva (PRAGMA + ALTER) das duas colunas
- [x] `app/schemas.py`: `parse_variaveis_deploy` + `validar_deploy` integrada em `validar_campos`

## Fase 2 — Provisionamento (D2) + API (green)

- [x] `app/provisioner.py`: `montar_comando` prefixa `export` (domínio/variáveis) com quoting seguro
- [x] `app/routers/api.py`: `_setup_para_json` + `_CHAVES_SETUP` incluem os novos campos

## Fase 3 — UI web + docs (green)

- [x] `app/routers/web.py`: campos em `CAMPOS` + Form (criar/editar)
- [x] `app/templates/setups/form.html`: campos `dominio` + `variaveis_deploy`
- [x] `app/templates/setups/detail.html`: exibir config de deploy
- [x] `README.md`: seção feature 009

## Fase 4 — Validação final

- [x] Suíte completa verde (**132 passed, 4 skip**) + `ruff` limpo
- [x] Commit `T054` + push

---

## Notes

- Sem segredos nos novos campos (FR-013/constituição IV); log sempre redigido.
- `AUTOMATIC1_DOMAIN` exportado quando `dominio` presente; variáveis exportadas quando houver.
