# Web Interface Contract: Provisionador Real

**Branch**: `004-provisioner` | **Date**: 2026-09-03 | **Spec**: [spec.md](../spec.md) | **Data model**: [data-model.md](../data-model.md)

Evolui o contrato das features `001`–`003` de forma **aditiva** (rotas novas; telas `003` ampliadas para exibir execução real).

## Rotas / Páginas (novas — 004)

| Método | Caminho | Página | Descrição | Origem |
|--------|---------|--------|-----------|--------|
| GET | `/setups/{setup_id}/provisionar?maquina={host_id}` | confirmação | Confirma o provisionamento real: mostra setup, máquina, `origem_asset`, hash (ou aviso "sem hash / integridade não verificada") e avisos de bloqueio | US1/US3 |
| POST | `/setups/{setup_id}/provisionar` | — (redirect) | Executa o provisionamento real (síncrono, via runner); em sucesso/erro cria `Execution` real e `303 → /setups/{setup_id}?sucesso=execucao_provisionada` | US1 |

**Disparo**: botão "⚡ Provisionar" no detalhe do setup (e no detalhe da máquina), com seleção de máquina ativa (reusa a lista de máquinas ativas).

## Alterações em telas existentes (`003`)

- Detalhe do setup e da máquina: execuções **reais** exibem `exit_code` e **log sanitizado** (bloco expandível); execuções manuais (`003`) continuam como estão.

## Regras de validação / guardas (server)

- **Guardas antes de executar** (FR-001/FR-002/FR-007): setup não `arquivado`; máquina `ativa`; sem `Execution` `em_andamento` para o mesmo par; credencial SSH configurada no ambiente (`AUTOMATIC1_SSH_USER`/`AUTOMATIC1_SSH_KEY`); `origem_asset` executável; `hash` (quando presente) confere. Qualquer guarda falha → **nenhuma execução** ocorre e mensagem acionável é exibida (HTTP 200 na página de confirmação, sem registro `Execution`).
- **Timeout** na execução; **log sanitizado** (segredos redigidos) antes de persistir/exibir (FR-005).

## Comportamentos transversais

- **Auditoria**: `Execution` real registra autor (`created_by`), horários e `exit_code` (FR-008).
- **Sem credenciais**: nenhuma credencial trafega/é armazenada via formulário (FR-004).
- **Idioma**: PT-BR.
