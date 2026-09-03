# Roda a suíte de testes (pytest) do Automatic1 Admin
$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path $PSScriptRoot -Parent
Set-Location $repoRoot

uv run pytest
