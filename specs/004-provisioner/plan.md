# Implementation Plan: Provisionador Real (004-provisioner)

**Branch**: `004-provisioner` | **Date**: 2026-09-03 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/004-provisioner/spec.md`

## Summary

Fazer o Automatic1 Admin **executar de fato** um setup numa máquina alvo (Debian + Docker Swarm). Um **runner** (abstração SSH plugável; `FakeRunner` em testes) roda o **asset referenciado por `origem_asset`** de forma segura e idempotente: guardas (setup/máquina/hash/credencial/concorrência), validação de integridade quando `hash` presente, **redação de segredos** no log, e gravação da `Execution` (feature `003`) com status real, `exit_code`, `log` e horários. **v1 síncrono com timeout**; sem filas; sem instalar por ferramenta (scripts instaladores = próxima feature).

## Technical Context

**Language/Version**: Python 3.11+ (mesma das features `001`–`003`).

**Primary Dependencies**: FastAPI; SQLModel; **paramiko** (novo — `SSHRunner` em produção; pinado). Jinja2. Dev/test: pytest, httpx.

**Storage**: SQLite local. Migração **aditiva idempotente** em `execution` (PRAGMA+ALTER) para `log`/`exit_code`/`started_at`/`finished_at` (padrão feature `002`). Sem mudança em `environment_setup`/`target_host`.

**Testing**: pytest + TestClient. Suíte nova `tests/test_provisioner.py` com **FakeRunner** (sem rede/SSH em CI) + regressão `001`–`003` zero. Test-first (constituição III).

**Target Platform**: Navegador moderno (admin interno); execução real atinge hosts Debian/Docker via SSH.

**Project Type**: Web application (admin interno) server-rendered + **executor/engine** interno (síncrono).

**Performance Goals**: Baixo volume; execuções curtas com timeout configurável; UI percebida < 1s (fora o tempo da execução).

**Constraints**: Nenhuma credencial no banco/UI (FR-004); log sempre sanitizado (FR-005); guardas de bloqueio sem efeito colateral (FR-002/FR-003/FR-007); concorrência máxima de 1 `em_andamento` por par (FR-007/SC-006); timeout (FR-007); auditoria/autor (FR-008).

**Scale/Scope**: Poucos operadores; dezenas de hosts; execuções síncronas no v1.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **G1 — Test-First (III)**: testes antes do core; validação automatizada. → Atendido (`FakeRunner` + suíte nova antes do engine; CI existente).
- **G2 — Automation & Reproducibility (I)**: bootstrap idempotente; migração aditiva idempotente; execução reproduzível. → Atendido.
- **G3 — Security (IV)**: **sem credenciais no banco** (ambiente/cofre); asset validado por hash quando disponível; **redação de segredos** em logs; dependência nova (`paramiko`) pinada e revisada. → Atendido (FR-003/FR-004/FR-005).
- **G4 — Simplicity & YAGNI (VII)**: runner único + FakeRunner; síncrono; sem fila/agente; sem "inventar" instalador por ferramenta. → Atendido.
- **G5 — Consistent UX (VI)**: confirmação, guardas com mensagens acionáveis, log exibido, PT-BR. → Atendido.
- **G6 — Observability & Versioning (VIII)**: log estruturado de cada execução (início/fim/exit code); SemVer. → Atendido.

**Resultado**: GATE **PASS** — sem violações. Reavaliado após a Fase 1: sem alterações (design aditivo + runner confirmados).

## Key Design Decisions (resumo — detalhe em research.md)

1. **Runner plugável**: `SSHRunner` (paramiko) em produção + `FakeRunner` em testes; execução síncrona com timeout — D1.
2. **Credenciais por ambiente**: `AUTOMATIC1_SSH_USER`/`AUTOMATIC1_SSH_KEY` (+passphrase nunca logada); ausência → bloqueio — D2.
3. **Executa o asset referenciado** (`origem_asset`), com verificação sha256 quando `hash` presente; origem não executável → bloqueio acionável — D3.
4. **Log sanitizado** (redação de segredos) antes de persistir/exibir — D4.
5. **Concorrência**: 1 `em_andamento` por par setup×máquina — D5.
6. **`Execution` evoluída** (colunas aditivas) + migração PRAGMA+ALTER — D6.
7. **`paramiko`** pinado (nova dependência runtime) — D7.
8. **UI**: ação "⚡ Provisionar" (confirmação → POST) + log no histórico `003` — D8.

## Project Structure

### Documentation (this feature)

```text
specs/004-provisioner/
├── spec.md / plan.md / research.md / data-model.md / quickstart.md
├── contracts/web.md
└── tasks.md   # Fase 2 (/speckit-tasks — NÃO criado aqui)
```

### Source Code (repository root)

```text
app/
├── config.py               # + leitura AUTOMATIC1_SSH_* (nunca logada)
├── database.py             # init_db: + migração aditiva em `execution` (PRAGMA+ALTER)
├── models.py               # Execution: + log/exit_code/started_at/finished_at (nullable)
├── provisioner.py          # NOVO — engine: guardas + runner protocol + hash/redação + execução
├── runners.py              # NOVO — SSHRunner (paramiko) + FakeRunner
├── schemas.py              # (estendido se necessário: helper de sanitização)
├── routers/web.py          # + GET/POST /setups/{id}/provisionar; detalhes exibem log/exit_code
└── templates/
    ├── setups/provisionar.html   # NOVO — confirmação
    ├── setups/detail.html        # + bloco log/exit_code nas execuções reais
    └── maquinas/detail.html      # + bloco log/exit_code nas execuções reais
tests/
└── test_provisioner.py     # NOVO — C1–C6 (US1–US3) com FakeRunner
```

**Structure Decision**: Continua o monólito server-rendered. O **engine** de provisionamento fica isolado em `app/provisioner.py` (responsabilidades: guardas, integridade, redação, orquestração) e os **adaptadores** de transporte em `app/runners.py` — separação que permite testar o engine inteiro com `FakeRunner` sem rede. Rotas/UI no router/templates existentes.

## Complexity Tracking

> Sem violações de constituição a justificar — GATE PASS sem ressalvas. A dependência `paramiko` e a migração aditiva de `execution` são as únicas adições e estão justificadas (D6/D7).
