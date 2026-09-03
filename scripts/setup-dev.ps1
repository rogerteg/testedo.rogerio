# Setup de desenvolvimento (idempotente) — Automatic1 Admin
$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path $PSScriptRoot -Parent
Set-Location $repoRoot

# 1) Ambiente virtual
if (-not (Test-Path '.venv')) {
    Write-Host "Criando ambiente virtual (.venv)..."
    uv venv
} else {
    Write-Host "Ambiente virtual já existe (.venv)."
}

# 2) Dependências (runtime + dev) sincronizadas
Write-Host "Sincronizando dependências..."
uv sync

# 3) Diretório de dados (banco SQLite local)
New-Item -ItemType Directory -Path 'data' -Force | Out-Null

# 4) Validação: app importável
Write-Host "Validando import da app..."
uv run python -c "import app.main; print('OK: app.main importável')"

Write-Host "Setup concluído. Execute: .\scripts\run.ps1"
