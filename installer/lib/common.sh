#!/usr/bin/env bash
# Automatic1 — helpers comuns do instalador (feature 005).
# Uso: `source` no início dos scripts de instalação.
set -euo pipefail

# Configuração padrão (sobrescrevível por variáveis de ambiente/config).
: "${AUTOMATIC1_STATE_DIR:=/var/lib/automatic1}"
: "${AUTOMATIC1_DRY_RUN:=0}"
AUTOMATIC1_MANIFESTO="${AUTOMATIC1_MANIFESTO:-${AUTOMATIC1_STATE_DIR}/manifesto.txt}"

log() { printf '[automatic1] %s\n' "$*"; }

die() { printf '[automatic1][erro] %s\n' "$*" >&2; exit 1; }

is_dry_run() { [ "${AUTOMATIC1_DRY_RUN:-0}" = "1" ]; }

require_root() {
  if [ "$(id -u)" -ne 0 ]; then
    die "Execute como root (ex.: sudo)."
  fi
}

require_debian_11_12() {
  if ! grep -qE '^ID=.?(debian)' /etc/os-release 2>/dev/null \
     || ! grep -qE 'VERSION_ID="(11|12)"' /etc/os-release 2>/dev/null; then
    die "Sistema deve ser Debian 11 ou 12."
  fi
}

estado_feito() { [ -f "${AUTOMATIC1_STATE_DIR}/$1.done" ]; }

marcar_feito() {
  mkdir -p "${AUTOMATIC1_STATE_DIR}"
  touch "${AUTOMATIC1_STATE_DIR}/$1.done"
}

registrar_manifesto() {
  mkdir -p "$(dirname "${AUTOMATIC1_MANIFESTO}")"
  printf '%s | %s | %s\n' "$1" "$2" "$3" | tee -a "${AUTOMATIC1_MANIFESTO}"
}
