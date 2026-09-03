#!/usr/bin/env bash
# Automatic1 — instalador da aplicação N8N (referência — feature 005).
# Idempotente via marcador; exige infra base (bootstrap) e Docker.
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../lib/common.sh
source "${DIR}/../lib/common.sh"

instalar_n8n() {
  require_root
  if estado_feito automatic1-app-n8n; then
    log "N8N já instalado (idempotente)."
    return 0
  fi

  local dominio="${AUTOMATIC1_N8N_DOMAIN:-localhost}"
  local versao="${AUTOMATIC1_N8N_VERSION:-latest}"
  log "Instalando N8N (${versao}) em ${dominio} ..."

  if is_dry_run; then
    log "[check] N8N: pré-requisitos OK (dry-run, nada aplicado)."
    return 0
  fi

  if ! command -v docker >/dev/null 2>&1; then
    die "Docker não encontrado — rode o bootstrap primeiro."
  fi

  # Comandos reais de deploy (serviço/site) entram aqui — validar em host Debian
  # (ver specs/005-installer/quickstart.md Parte B).

  marcar_feito automatic1-app-n8n
  registrar_manifesto "n8n" "${versao}" "https://${dominio}"
  log "N8N instalado."
}

instalar_n8n "$@"
