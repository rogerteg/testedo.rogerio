# Implementation Plan: Máquinas Alvo e Execuções (003-machines-runs)

**Branch**: `003-machines-runs` | **Date**: 2026-09-03 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/003-machines-runs/spec.md`

## Summary

Adicionar ao Automatic1 Admin o vínculo "**onde cada setup é provisionado**": cadastro/gestão de **máquinas alvo** (`TargetHost`) e de **execuções** (`Execution` — setup × máquina, registro/estado, sem execução real), com histórico pelos dois lados, **aviso de "utilização ativa"** no arquivamento/desativação e **última execução derivada** no detalhe do setup (Q3=A, com fallback manual da `001`). **Sem credenciais** (constituição IV); provisionamento real = Etapa 3 (`004`).

## Technical Context

**Language/Version**: Python 3.11+ (mesma das features `001`/`002`).

**Primary Dependencies**: FastAPI; SQLModel; Jinja2. Sem dependências novas.

**Storage**: SQLite local. Duas **tabelas novas** (`target_host`, `execution`) criadas por `create_all` no `init_db()` — **nenhuma coluna existente muda** (sem migração aditiva; regressão zero). FKs simples (`setup_id`, `target_host_id`).

**Testing**: pytest + TestClient (fixtures existentes). Suíte nova `tests/test_maquinas_execucoes.py` (C1–C7). Test-first (constituição III).

**Target Platform**: Navegador moderno — admin interno server-rendered (Jinja2).

**Project Type**: Web application (admin interno) server-rendered; monólito FastAPI.

**Performance Goals**: Baixo volume; operações percebidas < 1s.

**Constraints**: Sem credenciais (FR-004); execução = registro/estado, sem executar nada (FR-003/Q1); `resultado_ultima_execucao` derivado em leitura sem remover coluna (Q3); aviso (não bloqueio) no arquivamento/desativação com execuções (US3); auditoria autor+data; anti-segredo (FR-006).

**Scale/Scope**: Poucos administradores; dezenas de máquinas e execuções no v1.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **G1 — Test-First (III)**: testes antes do core; validação automatizada. → Atendido (suíte nova antes da rota/UI; CI existente).
- **G2 — Automation & Reproducibility (I)**: schema por `create_all` idempotente; scripts existentes. → Atendido.
- **G3 — Security (IV)**: **nenhuma credencial** em máquina/execução (apenas metadados); anti-segredo ativo. → Atendido (FR-004/SC-005).
- **G4 — Simplicity & YAGNI (VII)**: duas entidades novas simples (FKs + consultas manuais); sem executor real; sem edição/exclusão de execução. → Atendido.
- **G5 — Consistent UX (VI)**: mensagens acionáveis, avisos de confirmação, PT-BR. → Atendido.
- **G6 — Observability & Versioning (VIII)**: logging estruturado das operações; SemVer. → Atendido.

**Resultado**: GATE **PASS** — sem violações. Reavaliado após a Fase 1: sem alterações.

## Key Design Decisions (resumo — detalhe em research.md)

1. **Execução = registro/estado** (sem execução real; Etapa 3 fará o provisionamento) — D1.
2. **Máquina = apenas metadados** (sem credenciais/referências a segredo) — D2.
3. **`resultado_ultima_execucao` derivado em leitura** (última `Execution`; fallback manual da `001`) — sem remoção/migração — D3.
4. **Tabelas novas por `create_all`**; FKs simples; sem mudança em `environment_setup` — D4.
5. **Ciclo de vida**: máquina `ativa/inativa` via desativar/reativar (confirmação + aviso); execução imutável — D5.
6. **Validação reutilizando** `contem_segredo`/nome único; conjuntos/rótulos PT-BR — D6.
7. **UI**: páginas de máquinas; criação de execução no detalhe do setup; histórico nos dois lados; aviso no arquivamento — D7.

## Project Structure

### Documentation (this feature)

```text
specs/003-machines-runs/
├── spec.md / plan.md / research.md / data-model.md / quickstart.md
├── contracts/web.md
└── tasks.md   # Fase 2 (/speckit-tasks — NÃO criado aqui)
```

### Source Code (repository root)

```text
app/
├── models.py              # + TargetHost, Execution (novas tabelas)
├── schemas.py             # + status/labels máquina+execução; validar_maquina/validar_execucao
├── database.py            # create_all cobre tabelas novas (sem ALTER)
├── routers/web.py         # + rotas máquinas + execução + avisos + última execução derivada
└── templates/
    ├── setups/detail.html # + histórico de execuções + botão "Registrar execução"
    ├── setups/executar.html       # NOVO — form de execução
    ├── setups/arquivar.html       # + aviso de utilização ativa (contagem)
    └── maquinas/          # NOVO — list, form, detail, desativar
tests/
├── test_maquinas_execucoes.py  # NOVO — C1–C7 (US1–US3)
```

**Structure Decision**: Continua o monólito server-rendered. Novos modelos no mesmo `models.py`; validação centralizada em `schemas.py`; rotas de máquina/execução adicionadas ao router web existente (evita novo arquivo de router sem ganho — YAGNI). Templates de máquina em subpasta `maquinas/`.

## Complexity Tracking

> Sem violações de constituição a justificar — GATE PASS sem ressalvas.
