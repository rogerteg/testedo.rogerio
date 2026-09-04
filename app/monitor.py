"""Monitoramento/status dos serviços (feature 011) — leitura, sem persistir.

Consulta a saúde da stack de uma máquina alvo (Debian + Docker Swarm): estado do
nó e serviços (`docker node ls` + `docker service ls`). Somente leitura, sem
segredos (constituição IV); saída sanitizada via `redigir` antes de exibir.
"""
import os
from typing import TYPE_CHECKING

from .provisioner import redigir

if TYPE_CHECKING:  # evita import circular p/ type-check
    from .runners import Runner

TIMEOUT_PADRAO = 60


def montar_comando_status() -> str:
    """Comando somente leitura de status (docker node + services)."""
    return "docker node ls; echo '--- serviços ---'; docker service ls"


def consultar_status(runner: "Runner", host: str) -> dict:
    """Executa a consulta de status e retorna dict ``{ok, exit_code, saida}``.

    ``saida`` já sanitizada (segredos redigidos — FR-005). Erros de transporte
    viram ``ok=False`` com mensagem acionável.
    """
    timeout = int(os.getenv("AUTOMATIC1_SSH_TIMEOUT", str(TIMEOUT_PADRAO)))
    comando = montar_comando_status()
    try:
        resultado = runner.executar(comando=comando, host=host, timeout=timeout)
    except Exception as exc:  # noqa: BLE001 - transporte (rede/SSH)
        return {"ok": False, "exit_code": None, "saida": redigir(f"ERRO no transporte SSH: {exc}", [])}
    saida = redigir(resultado.output, [])
    return {"ok": resultado.exit_code == 0, "exit_code": resultado.exit_code, "saida": saida}
