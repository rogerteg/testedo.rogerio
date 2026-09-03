#!/usr/bin/env bash
# Automatic1 — entrada do instalador (feature 005).
# Headless: configuração por variáveis de ambiente (config.example.env).
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/common.sh
source "${DIR}/lib/common.sh"

VERSION="0.1.0"

uso() {
  cat <<EOF
Automatic1 Installer v${VERSION}

Uso:
  sudo ./install.sh            # executa bootstrap + apps de AUTOMATIC1_APPS
  sudo ./install.sh --check    # valida pré-requisitos sem aplicar mudanças
  ./install.sh --version       # exibe a versão
  ./install.sh --help          # este texto

Variáveis (AUTOMATIC1_*): consulte config.example.env.
Exit codes: 0 sucesso; 1 erro; 2 pré-requisito ausente; 3 config inválida.
EOF
}

main() {
  local modo="run"
  case "${1:-}" in
    --version)
      log "automatic1-installer ${VERSION}"
      return 0
      ;;
    --help | -h)
      uso
      return 0
      ;;
    --check)
      AUTOMATIC1_DRY_RUN=1
      modo="check"
      ;;
    "" | run) : ;;
    *)
      die "Argumento desconhecido: ${1:-} (use --help)."
      ;;
  esac

  if [ "${AUTOMATIC1_BOOTSTRAP:-1}" = "1" ]; then
    log "Etapa: bootstrap da infraestrutura base."
    "${DIR}/bootstrap.sh"
  fi

  local apps="${AUTOMATIC1_APPS:-}"
  if [ -n "${apps}" ]; then
    for app in ${apps}; do
      if [ -f "${DIR}/apps/${app}.sh" ]; then
        log "Instalando aplicação: ${app}"
        "${DIR}/apps/${app}.sh"
      else
        log "Aplicação '${app}' ainda sem instalador próprio — ignorada (adoção incremental)."
      fi
    done
  elif [ "${modo}" != "check" ]; then
    log "Nenhuma aplicação em AUTOMATIC1_APPS (opcional)."
  fi

  log "Instalador concluído. Manifesto: ${AUTOMATIC1_MANIFESTO}"
}

main "$@"
