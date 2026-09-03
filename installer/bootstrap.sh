#!/usr/bin/env bash
# Automatic1 — bootstrap idempotente da infraestrutura base (feature 005).
# Escopo do v1 (framework): Docker + Docker Swarm.
# Traefik/Portainer e serviços de apoio: passos a validar em host Debian
# (ver installer/apps/README.md e specs/005-installer/quickstart.md).
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/common.sh
source "${DIR}/lib/common.sh"

instalar_docker() {
  if command -v docker >/dev/null 2>&1; then
    log "Docker já instalado (idempotente)."
    return 0
  fi
  log "Instalando Docker (canal oficial)..."
  if is_dry_run; then
    log "[check] Instalação do Docker (dry-run, nada aplicado)."
    return 0
  fi
  curl -fsSL https://get.docker.com | sh
  systemctl enable --now docker >/dev/null 2>&1 || true
}

iniciar_swarm() {
  if is_dry_run; then
    log "[check] Docker Swarm (dry-run)."
    return 0
  fi
  estado=$(docker info --format '{{.Swarm.LocalNodeState}}' 2>/dev/null || echo inactive)
  if [ "$estado" != "active" ]; then
    log "Iniciando Docker Swarm..."
    docker swarm init || die "Falha ao iniciar o Docker Swarm."
  else
    log "Docker Swarm já ativo (idempotente)."
  fi
}

bootstrap() {
  require_root
  if estado_feito automatic1-bootstrap; then
    log "Bootstrap já realizado (idempotente)."
    return 0
  fi
  instalar_docker
  iniciar_swarm
  if is_dry_run; then
    log "[check] Bootstrap: pré-requisitos OK (dry-run, nada aplicado)."
    return 0
  fi
  marcar_feito automatic1-bootstrap
  registrar_manifesto "automatic1" "bootstrap-infra" "docker+swarm"
  log "Bootstrap da infraestrutura base concluído."
}

bootstrap "$@"
