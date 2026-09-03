# Quickstart: Instalador Próprio do Automatic1 (validação)

**Branch**: `005-installer` | **Date**: 2026-09-03 | **Spec**: [spec.md](spec.md)

Guia de validação. Detalhes em [data-model.md](data-model.md) e [contracts/cli.md](contracts/cli.md). Implementação em `tasks.md`.

## Parte A — Validação automatizada (sem host Debian)

```powershell
.\scripts\test.ps1          # inclui tests/test_installer.py (estrutural + anti-segredo)
# sintaxe bash (se bash disponível):
bash -n installer/install.sh installer/bootstrap.sh installer/lib/common.sh installer/apps/*.sh
```

- **Esperado**: arquivos `.sh` presentes/consistentes, sem segredos (`contem_segredo`), sintaxe OK (quando `bash` existe).

## Parte B — Validação E2E real (host Debian 11/12 — manual)

> A execução real de bootstrap/apps **exige um host Debian 11/12 de teste** (VPS/contêner); não roda neste ambiente (Windows/CI). Condição registrada na constituição.

1. Copiar `installer/` para o host (ou `git clone`).
2. `cd installer && cp config.example.env .env` e ajustar `AUTOMATIC1_DOMAIN` etc. (sem segredos embutidos).
3. `sudo ./install.sh --check` → exit `0` se pré-requisitos OK.
4. `sudo env $(cat .env) ./install.sh` → bootstrap + apps de `AUTOMATIC1_APPS`.
5. Rodar de novo → **idempotente** (0 efeitos duplicados); conferir `manifesto.txt`.
6. Invalidar (ex.: `AUTOMATIC1_DOMAIN` vazio com app que exige domínio) → exit `3`, mensagem clara.

## Critérios de aceite automatizados (mapeamento)

| Teste (proposto) | Cobre |
|------------------|-------|
| `tests/test_installer.py` | estrutura, anti-segredo, sintaxe (quando bash) — C1–C3/FR-001–FR-005 (parte) |
| Manual (host Debian) | E2E real — C1–C3 (parte restante), SC-001/SC-002/SC-005 |
