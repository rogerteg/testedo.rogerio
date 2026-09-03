# Research: Instalador Próprio do Automatic1 (005)

**Branch**: `005-installer` | **Date**: 2026-09-03 | **Spec**: [spec.md](spec.md)

Fase 0 do `/speckit-plan`. Resolve Q1–Q3 (A/A/A) e desenha o instalador. Formato: *Decision / Rationale / Alternatives considered*.

---

## D1 — Formato/entrega (Q1=A)

- **Decision**: Instalador como **scripts versionados no repo do Automatic1**, executados no VPS pelo operador (pull): `installer/install.sh` (entrada/orquestrador) + `installer/lib/common.sh` (helpers) + `installer/bootstrap.sh` (infra base) + `installer/apps/<ferramenta>.sh` (apps). Sem geração sob demanda nesta etapa.
- **Rationale**: Simples, auditável e versionado (constituição II); estilo SetupFrancisMno (referência aprovada); testável estruturalmente e em host Debian dedicado.
- **Alternatives considered**: Gerado sob demanda pelo Admin (exige transporte seguro + composição dinâmica — adiado); híbrido (maior escopo).

## D2 — Autoria dos scripts (Q2=A, incremental)

- **Decision**: O Automatic1 passa a **possuir scripts instaladores próprios por ferramenta** (código no repo). Adoção **incremental**: a primeira entrega cobre o **framework** (lib + bootstrap de infra + apps de referência) e a **validação automatizada**; as demais ferramentas são incrementais. Quando os scripts estiverem hospedados (repo publicado), o catálogo (`002`) passará a referenciá-los como `origem_asset` (destravando o provisionador `004`).
- **Rationale**: Controle/idempotência; evita depender de terceiros (constituição IV). **Honestidade**: os scripts reais de Debian/Docker exigem um **host Debian** para validação E2E — não executáveis neste ambiente (Windows/CI); a validação automatizada aqui é estrutural/estática (ver D5).
- **Alternatives considered**: Embrulhar scripts de terceiros (dependência + revisão cara — rejeitado); tentar escrever 15 instaladores sem host de validação (não verificável — rejeitado).

## D3 — Configuração headless (Q3=A)

- **Decision**: Instalador **headless**: configuração por **variáveis de ambiente/arquivo** com defaults seguros (`AUTOMATIC1_*`); sem passos interativos obrigatórios. Menu interativo é extra opcional (fora do v1).
- **Rationale**: Constituição I (automação headless) e testável em CI.
- **Alternatives considered**: Menu numérico estilo SetupFrancisMno (reduz headless — rejeitado para v1).

## D4 — Estrutura e comportamento do instalador

- **Decision**: `install.sh` orquestra: `--help`/`--version`/`--check` (pré-requisitos) e execução; carrega config; chama `bootstrap.sh` (infra: Docker + Swarm + Traefik + Portainer + Postgres/Mongo/Redis) e apps listados; gera **manifesto** (serviço/versão/URL) em stdout/arquivo. Scripts: `#!/usr/bin/env bash`, `set -euo pipefail`, helpers de log/erro, **idempotência por marcadores de estado** e verificação de pré-requisitos (root/sudo, portas, docker).
- **Rationale**: Reproduzível/idempotente (constituição I/V), saída clara com exit codes (VI), sem segredos (IV).
- **Alternatives considered**: Um único script monolítico (difícil de manter/testar — rejeitado).

## D5 — Validação (limitação honesta)

- **Decision**: Camada de validação **automatizada sem host Debian**: (1) testes Python estruturais (arquivos `.sh` presentes, shebang, `source` correto, `contem_segredo` não detecta segredos no conteúdo — FR-013/IV); (2) `bash -n` (sintaxe) quando `bash` disponível; (3) consistência do manifesto/catálogo quando aplicável. A validação **E2E real** (bootstrap/apps num Debian) fica documentada no `quickstart.md` como passo **manual em host de teste** — condição registrada na constituição ("não rodou na minha máquina não basta" → exige host real).
- **Rationale**: G1/III dentro do que este ambiente permite; transparência sobre o que é (ou não) verificado.
- **Alternatives considered**: Não entregar (pararia o roadmap); fingir validação E2E (desonesto — rejeitado).

## D6 — Interação com as demais features

- **Decision**: Nenhuma mudança de schema/entidade. O instalador é **código shell** no repo (`installer/`); a integração com o catálogo (`origem_asset`) e com o Admin/`004` ocorre quando os scripts estiverem hospedados (fora do v1 desta feature, documentado).
- **Rationale**: Mantém escopo contido; evita apontar o catálogo para URLs que ainda não existem.
