# Implementation Plan: Instalador Próprio do Automatic1 (005-installer)

**Branch**: `005-installer` | **Date**: 2026-09-03 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/005-installer/spec.md`

## Summary

Entregar o **instalador cliente do Automatic1** para VPS Debian 11/12: scripts **versionados no repo** (`installer/`) com bootstrap idempotente da infra base (Docker/Swarm/Traefik/Portainer + Postgres/Mongo/Redis) e instalação de apps do catálogo por **scripts instaladores próprios** (`apps/*.sh`), **headless** (config + env, defaults seguros) e com **manifesto** de saída. **Adoção incremental**: o v1 cobre o framework (lib + bootstrap + apps de referência) + validação estrutural/estática; scripts por ferramenta adicionais e a ligação `catálogo → origem_asset` entram quando hospedados. *Exceção de runtime registrada: PowerShell → bash/Debian (o produto provisiona hosts Linux).*

## Technical Context

**Language/Runtime**: **bash** (Debian 11/12); testes estruturais em Python (pytest). Exceção ao default PowerShell da constituição, justificada e registrada (D1/D4).

**Primary Dependencies**: Nenhuma nova dependência Python. Scripts usam ferramentas padrão do Debian (`curl`, `docker`).

**Storage**: Nenhuma mudança no banco. Estado de idempotência + manifesto em `AUTOMATIC1_STATE_DIR` (`/var/lib/automatic1`).

**Testing**: `tests/test_installer.py` (estrutural: arquivos, shebang, anti-segredo via `contem_segredo`, consistência `config.example.env`); `bash -n` quando `bash` disponível (skip se ausente). E2E real = manual em host Debian (`quickstart.md` Parte B).

**Target Platform**: VPS Debian 11/12 (execução pelo operador no host — pull).

**Project Type**: Instalador/scripts shell (automação de ambiente) — complementa a web app do Admin.

**Performance Goals**: Bootstrap em < 15 min num host de teste; idempotente.

**Constraints**: Headless (Q3=A); sem segredos embutidos (IV); exit codes padronizados; manifesto auditável (SC-005); validação honesta (sem E2E neste ambiente — registrado).

**Scale/Scope**: Framework + bootstrap + apps de referência no v1; demais ferramentas incrementais (Q2=A).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **G1 — Test-First (III)**: validação automatizada (estrutural/sintaxe) + validação E2E documentada em host real. → Atendido (dentro do que o ambiente permite; limitação honesta em D5).
- **G2 — Automation & Reproducibility (I)**: scripts headless, idempotentes, com marcadores de estado. → Atendido.
- **G3 — Security (IV)**: sem segredos embutidos; configuração sensível por env/arquivo; anti-segredo nos testes. → Atendido.
- **G4 — Simplicity & YAGNI (VII)**: framework enxuto; adoção incremental; sem geração sob demanda no v1. → Atendido.
- **G5 — Consistent UX (VI)**: logs prefixados `[automatic1]`, exit codes, manifesto legível. → Atendido.
- **G6 — Observability & Versioning (VIII)**: `--version`; manifesto por execução; scripts versionados. → Atendido.

**Resultado**: GATE **PASS** — sem violações; **exceção de runtime (bash/Debian) registrada** e justificada.

## Key Design Decisions (resumo — detalhe em research.md)

1. Scripts no repo, executados no VPS (Q1=A) — D1.
2. Scripts instaladores **próprios**, adoção incremental (Q2=A) — D2.
3. Headless via config/env (Q3=A) — D3.
4. Estrutura: `install.sh` + `lib/common.sh` + `bootstrap.sh` + `apps/*.sh` + `config.example.env` — D4.
5. Validação estrutural (sem host) + E2E manual documentada — D5.
6. Sem mudança de banco; ligação catálogo→origem quando hospedado — D6.

## Project Structure

### Documentation (this feature)

```text
specs/005-installer/
├── spec.md / plan.md / research.md / data-model.md / quickstart.md
├── contracts/cli.md
└── tasks.md   # Fase 2 (/speckit-tasks — NÃO criado aqui)
```

### Source Code (repository root)

```text
installer/
├── install.sh              # NOVO — entrada/orquestrador (headless)
├── lib/common.sh           # NOVO — helpers (log/erro/require_root/config/estado/manifesto)
├── bootstrap.sh            # NOVO — infra base idempotente (Docker/Swarm/Traefik/Portainer + apoio)
├── apps/
│   ├── n8n.sh              # NOVO — app de referência (exemplo idempotente)
│   └── README.md           # NOVO — como adicionar novas ferramentas (padrão)
├── config.example.env      # NOVO — variáveis AUTOMATIC1_* com defaults seguros
tests/
└── test_installer.py       # NOVO — validação estrutural/anti-segredo/sintaxe
```

**Structure Decision**: Código shell autocontido em `installer/` (independente da web app), com layout claro para adição incremental de ferramentas. Validação estrutural em Python para CI (sem host Debian).

## Complexity Tracking

> Sem violações de constituição a justificar além da **exceção de runtime (PowerShell → bash/Debian)**, justificada (o produto provisiona hosts Linux/Debian) e registrada na spec/plan.
