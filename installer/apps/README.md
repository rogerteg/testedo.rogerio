# Automatic1 — apps instaladores (feature 005)

Cada aplicação do catálogo tem um instalador próprio idempotente neste diretório
(`<ferramenta>.sh`). Adoção é **incremental** (nem todas as ferramentas na
primeira entrega).

## Padrão para adicionar uma ferramenta

1. Crie `apps/<ferramenta>.sh` com:

   ```bash
   #!/usr/bin/env bash
   set -euo pipefail
   DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
   source "${DIR}/../lib/common.sh"

   instalar_<ferramenta>() {
     require_root
     if estado_feito automatic1-app-<ferramenta>; then
       log "<Ferramenta> já instalada (idempotente)."
       return 0
     fi
     # ... passos reais de deploy (validar em host Debian) ...
     marcar_feito automatic1-app-<ferramenta>
     registrar_manifesto "<ferramenta>" "${versao}" "https://${dominio}"
   }
   instalar_<ferramenta> "$@"
   ```

2. Documente as variáveis `AUTOMATIC1_*` usadas em `../config.example.env`.
3. (Quando hospedado) atualize o catálogo (`002`) para referenciar o script como
   `origem_asset`.

## Validação

- Estrutural/anti-segredo/sintaxe: `tests/test_installer.py` + `bash -n`.
- **E2E real exige um host Debian 11/12 de teste** (VPS/contêiner) — ver
  `specs/005-installer/quickstart.md` Parte B. Aqui não há Docker/Swarm.
