# Quickstart: Provisionador Real (validação)

**Branch**: `004-provisioner` | **Date**: 2026-09-03 | **Spec**: [spec.md](spec.md)

Guia de **validação ponta a ponta**. Detalhes em [data-model.md](data-model.md) e [contracts/web.md](contracts/web.md). Implementação em `tasks.md`.

## Pré-requisitos

- Python 3.11+, PowerShell, `uv sync`. Nenhuma máquina real necessária na validação automatizada (usa `FakeRunner`).
- Para teste manual real (opcional): máquina Debian/Docker Swarm alcançável + `AUTOMATIC1_SSH_USER`/`AUTOMATIC1_SSH_KEY` no ambiente do Admin.

## Setup

```powershell
.\scripts\setup-dev.ps1
.\scripts\test.ps1     # suíte (provisioner via FakeRunner)
.\scripts\run.ps1      # http://127.0.0.1:8000
```

## Cenários de validação

### C1 — Provisionar com sucesso (US1-AS1 — FakeRunner)
1. Cadastrar um setup com `origem_asset` = script executável e uma máquina ativa.
2. No detalhe do setup, "⚡ Provisionar" → confirmar.
- **Esperado**: `Execution` real criada (status `sucesso`, `exit_code`, horários, log sanitizado); histórico exibe o resultado.

### C2 — Falha com log de motivo (US1-AS2)
1. FakeRunner configurado p/ falhar (ou hash divergente).
- **Esperado**: `Execution` com status `erro` e log contendo o motivo; **nenhum segredo** no log.

### C3 — Guardas (US1-AS4/US3-AS1/AS2/FR-007)
1. Setup arquivado, máquina inativa, par já `em_andamento`, credencial ausente ou `origem_asset` não executável.
- **Esperado**: **bloqueio** com mensagem acionável; nenhuma `Execution` criada.

### C4 — Integridade (US3-AS1/FR-003)
1. Setup com `hash` divergente do asset.
- **Esperado**: execução **bloqueada** antes de rodar, sem efeito colateral. Sem `hash` → executa com aviso registrado.

### C5 — Redação de segredo (US3-AS3)
- **Esperado (suíte)**: log com trecho que parece segredo é persistido/exibido **redigido**.

### C6 — Reexecução (US2-AS2)
1. Após erro, corrigir e reexecutar.
- **Esperado**: nova `Execution` com novo resultado; **histórico anterior preservado** (idempotente).

## Critérios de aceite automatizados (mapeamento)

| Teste (proposto) | Cobre |
|------------------|-------|
| `tests/test_provisioner.py` | C1–C6 (US1–US3) + regressão 001–003 |

## Fora do escopo deste guia

Instalador próprio por ferramenta (scripts `.sh` gerados/orquestrados pelo catálogo) — feature instalador (próxima etapa do roadmap). Execução real via SSH exige credenciais de ambiente e rede (não usadas em CI).
