# Sobe o servidor local do Automatic1 Admin
$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path $PSScriptRoot -Parent
Set-Location $repoRoot

uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
