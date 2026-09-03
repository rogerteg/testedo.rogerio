"""Testes unitários de validação (T041: limites máximos dos campos opcionais).

Test-First: DEVEM falhar (red) antes da implementação dos limites em
``app/schemas.py::validar_campos`` e passar após ela.
"""
import pytest

from app.schemas import validar_campos


def _base() -> dict:
    return {
        "nome": "Setup válido",
        "plataforma_alvo": "Windows",
        "origem_asset": "https://github.com/exemplo/setup",
        "status": "rascunho",
    }


@pytest.mark.parametrize(
    "campo, limite",
    [
        ("descricao", 2000),
        ("versao", 64),
        ("hash", 256),
        ("licenca", 500),
        ("resultado_ultima_execucao", 1000),
    ],
)
def test_campo_optional_ultrapassa_limite_retorna_erro(campo: str, limite: int) -> None:
    dados = _base()
    dados[campo] = "x" * (limite + 1)
    erros = validar_campos(dados)
    assert campo in erros
    assert "no máximo" in erros[campo].lower()


@pytest.mark.parametrize(
    "campo, limite",
    [
        ("descricao", 2000),
        ("versao", 64),
        ("hash", 256),
        ("licenca", 500),
        ("resultado_ultima_execucao", 1000),
    ],
)
def test_campo_optional_no_limite_nao_gera_erro(campo: str, limite: int) -> None:
    dados = _base()
    if campo == "versao":
        dados[campo] = "1.2.3"  # SemVer válida, muito abaixo do limite
    else:
        dados[campo] = "x" * limite
    erros = validar_campos(dados)
    assert campo not in erros
