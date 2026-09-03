"""Testes da auditoria de segredos (T042 / SC-005).

Test-First: DEVEM falhar (red) antes da implementação de
``app/security_audit.auditar_segredos``.
"""
import sqlite3

import pytest

from app.security_audit import auditar_segredos

_SCHEMA = """
CREATE TABLE environment_setup (
    id INTEGER PRIMARY KEY,
    nome TEXT, descricao TEXT, plataforma_alvo TEXT, origem_asset TEXT,
    versao TEXT, hash TEXT, licenca TEXT, status TEXT,
    resultado_ultima_execucao TEXT,
    created_at TEXT, updated_at TEXT, created_by TEXT, updated_by TEXT
);
"""


@pytest.fixture
def db_path(tmp_path):
    path = tmp_path / "audit.db"
    conn = sqlite3.connect(path)
    conn.execute(_SCHEMA)
    conn.executemany(
        "INSERT INTO environment_setup (id, nome, descricao, plataforma_alvo,"
        " origem_asset, versao, hash, licenca, status, resultado_ultima_execucao)"
        " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        [
            (1, "Setup limpo", "Descrição normal", "Windows",
             "https://github.com/exemplo/setup", "1.2.3", None, "MIT",
             "rascunho", None),
            (2, "Setup com segredo", "config com password=abc123", "Linux",
             "https://github.com/exemplo/outro", None, None, None,
             "rascunho", None),
        ],
    )
    conn.commit()
    conn.close()
    return path


def test_auditoria_detecta_segredo(db_path):
    violacoes = auditar_segredos(db_path)
    assert any(v["id"] == 2 for v in violacoes)


def test_auditoria_nao_acusa_registro_limpo(db_path):
    violacoes = auditar_segredos(db_path)
    assert not any(v["id"] == 1 for v in violacoes)


def test_auditoria_reports_o_campo_violado(db_path):
    violacoes = auditar_segredos(db_path)
    segredo = [v for v in violacoes if v["id"] == 2]
    assert segredo and segredo[0]["campo"] == "descricao"
