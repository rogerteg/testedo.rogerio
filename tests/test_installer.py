"""Testes estruturais da feature 005 — Instalador Próprio do Automatic1.

Sem host Debian: validam estrutura, consistência e anti-segredo dos scripts.
Sintaxe via `bash -n` quando o bash está disponível (skip caso contrário).
"""
import re
import shutil
import subprocess
from pathlib import Path

import pytest

from app.schemas import contem_segredo

RAIZ = Path(__file__).resolve().parents[1]
INSTALLER = RAIZ / "installer"

SCRIPTS = [
    "install.sh",
    "bootstrap.sh",
    "lib/common.sh",
    "apps/n8n.sh",
]
TEXTOS = [
    "install.sh",
    "bootstrap.sh",
    "lib/common.sh",
    "apps/n8n.sh",
    "config.example.env",
    "apps/README.md",
]


def test_estrutura_do_instalador():
    for rel in [*SCRIPTS, "config.example.env", "apps/README.md"]:
        assert (INSTALLER / rel).is_file(), f"arquivo ausente: installer/{rel}"


@pytest.mark.parametrize("rel", SCRIPTS)
def test_scripts_tem_shebang(rel):
    conteudo = (INSTALLER / rel).read_text(encoding="utf-8")
    assert conteudo.startswith("#!/usr/bin/env bash"), f"{rel} sem shebang bash"


@pytest.mark.parametrize("rel", TEXTOS)
def test_instalador_sem_segredos(rel):
    # FR-013 / constituição IV — nenhum script/config contém sinais de segredo.
    conteudo = (INSTALLER / rel).read_text(encoding="utf-8")
    assert not contem_segredo(conteudo), f"possível segredo detectado em installer/{rel}"


def test_config_example_documenta_variaveis_usadas():
    cfg = (INSTALLER / "config.example.env").read_text(encoding="utf-8")
    documentadas = set(re.findall(r"^(AUTOMATIC1_[A-Z0-9_]+)=", cfg, flags=re.MULTILINE))
    assert documentadas, "config.example.env sem variáveis AUTOMATIC1_*"

    usadas = set()
    for rel in SCRIPTS:
        usadas |= set(re.findall(r"AUTOMATIC1_[A-Z0-9_]+", (INSTALLER / rel).read_text(encoding="utf-8")))
    nao_documentadas = usadas - documentadas
    assert not nao_documentadas, f"variáveis usadas e não documentadas: {sorted(nao_documentadas)}"


@pytest.mark.skipif(
    shutil.which("bash") is None
    or subprocess.run(["bash", "-c", "exit 0"], capture_output=True, check=False).returncode != 0,
    reason="bash indisponível ou inutilizável neste ambiente",
)
@pytest.mark.parametrize("rel", SCRIPTS)
def test_sintaxe_bash_n(rel):
    resultado = subprocess.run(
        ["bash", "-n", str(INSTALLER / rel)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert resultado.returncode == 0, f"sintaxe inválida em {rel}: {resultado.stderr}"
