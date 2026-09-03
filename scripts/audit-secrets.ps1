# Auditoria de segredos nos registros do catálogo (T042 / SC-005)
# Uso: .\scripts\audit-secrets.ps1        (usa DB_PATH ou data\setups.db)
#      .\scripts\audit-secrets.ps1 C:\caminho\setups.db
$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path $PSScriptRoot -Parent
Set-Location $repoRoot

if ($args.Count -gt 0) {
    uv run python scripts/audit_secrets.py $args[0]
}
else {
    uv run python scripts/audit_secrets.py
}
