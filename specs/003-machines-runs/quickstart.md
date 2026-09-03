# Quickstart: Máquinas Alvo e Execuções (validação)

**Branch**: `003-machines-runs` | **Date**: 2026-09-03 | **Spec**: [spec.md](spec.md)

Guia de **validação ponta a ponta** da feature. Detalhes em [data-model.md](data-model.md) e [contracts/web.md](contracts/web.md). Implementação detalhada em `tasks.md`.

## Pré-requisitos

- Python 3.11+ e PowerShell. Nenhum serviço externo. SQLite local.

## Setup (idempotente)

```powershell
.\scripts\setup-dev.ps1
.\scripts\test.ps1
.\scripts\run.ps1     # http://127.0.0.1:8000
```

## Cenários de validação

### C1 — Cadastrar máquina alvo (US1-AS1/AS2)
1. Em `/maquinas`, clicar em nova máquina; preencher nome (`srv-prod-01`) e identificação (`203.0.113.10`).
- **Esperado**: máquina criada (default plataforma `Debian + Docker Swarm`, status `ativa`); nome duplicado/campo ausente → erro por campo, dados preservados.

### C2 — Sem credenciais (US1-AS4/FR-004)
1. Conferir formulário e detalhe da máquina.
- **Esperado**: **nenhum** campo de senha/token/chave; anti-segredo bloqueia texto com "password"/"token=" no cadastro.

### C3 — Registrar execução (US2-AS1/AS3)
1. Em um setup com histórico vazio, clicar "Registrar execução"; escolher máquina ativa + status (`sucesso`) + resumo.
- **Esperado**: execução criada com autor/data; aparece no **histórico do setup** e no **detalhe da máquina**.

### C4 — Última execução derivada (US2-AS4 / Q3=A)
1. Abrir o detalhe do setup que recebeu a execução (C3).
- **Esperado**: "última execução" exibida a partir do histórico (status/resumo/data); setup sem execução mostra o fallback manual da feature `001`.

### C5 — Aviso de utilização ativa no arquivamento (US3)
1. Setup **com** execução (C3): abrir "Arquivar".
- **Esperado**: aviso explícito com a contagem de execuções antes de confirmar; sem execuções → fluxo normal.

### C6 — Desativar máquina com aviso (US3)
1. Máquina **com** execuções → "Desativar".
- **Esperado**: aviso com contagem; confirmação desativa (`status=inativa`); cancelamento não altera. "Reativar" volta para `ativa`.

### C7 — Validação de execução (US2-AS2)
- **Esperado (suíte)**: status inválido ou máquina inexistente → erro claro, nada criado.

## Critérios de aceite automatizados (mapeamento)

| Teste (proposto) | Cobre |
|------------------|-------|
| `tests/test_maquinas_execucoes.py` | C1–C7 (US1–US3) + regressão 001/002 |

## Fora do escopo deste guia

Execução real (provisionamento via SSH/comandos) **não** é validada — pertence à Etapa 3 (`004`).
