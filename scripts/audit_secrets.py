"""CLI de auditoria de segredos do catálogo (T042).

Uso:
    uv run python scripts/audit_secrets.py                # usa DB_PATH ou data/setups.db
    uv run python scripts/audit_secrets.py <caminho.db>   # banco específico

Exit code: 0 = nenhum segredo; 1 = violações encontradas (útil p/ CI).
"""
import os
import sys
from pathlib import Path

# Garante que o pacote `app` seja importável ao rodar como script.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.security_audit import main

if __name__ == "__main__":
    db_path = sys.argv[1] if len(sys.argv) > 1 else os.getenv("DB_PATH")
    raise SystemExit(main(db_path))
