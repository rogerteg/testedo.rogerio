---

description: "Task list for Execução Assíncrona do Provisionamento (008-async-provisioning)"
---

# Tasks: Execução Assíncrona do Provisionamento

**Input**: Design documents from `specs/008-async-provisioning/`

**Status**: ✅ **Concluído** — `tests/test_async_provisioning.py` verde (7 testes) + regressão completa (**119 passed, 4 skip**) + `ruff` limpo.

**Decisões**: Q1=A fila em processo (threads) · Q2=A polling · Q3=A disparo imediato + consulta por id.

## Format: `[ID] [P?] [Story] Description`

---

## Fase única (planejada + executada)

- [x] Refatorar `app/provisioner.py`: `iniciar_execucao` (guardas + cria `em_andamento`) e `concluir_execucao` (roda runner → terminal); `provisionar` = wrapper síncrono (compat 004)
- [x] Criar `app/worker.py`: fila em threads, `enfileirar`, `provisionamento_assincrono` (`AUTOMATIC1_ASYNC`), `_recuperar_orfas_em`/`recuperar_orfas`
- [x] `app/routers/web.py`: rota de provisionamento assíncrona (inicia + enfileira; `sucesso=execucao_iniciada`); síncrona quando `AUTOMATIC1_ASYNC=0`
- [x] `app/main.py`: `recuperar_orfas()` no startup (execuções órfãs → interrompidas)
- [x] UI: auto-refresh (`meta http-equiv=refresh`) no detalhe quando há `em_andamento`
- [x] API: `GET /api/execucoes/{id}` (detalhe com log sanitizado) p/ polling
- [x] `tests/conftest.py`: `AUTOMATIC1_ASYNC=0` (regressão 004 determinística)
- [x] `tests/test_async_provisioning.py` (7 testes)
- [x] `README.md` + `render.yaml` env (`AUTOMATIC1_ASYNC`/`WORKERS`)

---

## Notes

- Concorrência 1 `em_andamento` por par mantida (guardas `004`)
- Sem fila externa (v1); recuperação de órfãs no startup
- Log sanitizado e auditoria mantidos
