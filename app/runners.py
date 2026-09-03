"""Adaptadores de execução do provisionador real (feature 004).

`Runner` é uma abstração plugável: `SSHRunner` executa remotamente (produção,
via paramiko) e `FakeRunner` simula (testes — sem rede/SSH em CI).
Nenhuma credencial é persistida ou logada aqui.
"""
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass
class RunResult:
    """Resultado bruto de uma execução (saída ainda NÃO sanitizada)."""

    exit_code: int
    output: str


class Runner(Protocol):
    def executar(self, *, comando: str, host: str, timeout: int) -> RunResult: ...


class FakeRunner:
    """Runner simulado para testes — não toca rede."""

    def __init__(self, resultados: list[RunResult] | None = None) -> None:
        self.resultados = list(resultados) if resultados else []
        self.chamadas: list[dict] = []

    def executar(self, *, comando: str, host: str, timeout: int = 0) -> RunResult:
        self.chamadas.append({"comando": comando, "host": host})
        if self.resultados:
            return self.resultados.pop(0)
        return RunResult(exit_code=0, output="Execução simulada concluída (fake).")


class SSHRunner:
    """Executa o comando no host remoto via SSH (paramiko). Credenciais por ambiente."""

    def __init__(
        self,
        *,
        user: str,
        key_path: str,
        passphrase: str | None = None,
        timeout: int = 300,
    ) -> None:
        self.user = user
        self.key_path = key_path
        self.passphrase = passphrase
        self.timeout = timeout

    def executar(self, *, comando: str, host: str, timeout: int | None = None) -> RunResult:
        import paramiko  # import tardio mantém o carregamento do módulo leve

        limite = timeout or self.timeout
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(
            hostname=host,
            username=self.user,
            key_filename=self.key_path,
            passphrase=self.passphrase,
            timeout=min(limite, 30),
            banner_timeout=30,
            allow_agent=False,
            look_for_keys=False,
        )
        try:
            _stdin, stdout, stderr = client.exec_command(comando, timeout=limite, get_pty=False)
            out = stdout.read().decode("utf-8", errors="replace")
            err = stderr.read().decode("utf-8", errors="replace")
            exit_status = stdout.channel.recv_exit_status()
        finally:
            client.close()

        output = out
        if err and err not in out:
            output = f"{out}\n{err}".strip()
        return RunResult(exit_code=exit_status, output=output)


def criar_runner() -> Runner | None:
    """Cria o runner ativo com base no ambiente (chamado por request — leitura de env direta).

    - ``AUTOMATIC1_RUNNER=fake`` → FakeRunner (testes/demo, sem rede);
    - ``AUTOMATIC1_SSH_KEY`` presente e arquivo válido → SSHRunner;
    - senão → ``None`` (guarda: credencial não configurada — sem execução).
    """
    if os.getenv("AUTOMATIC1_RUNNER", "ssh") == "fake":
        return FakeRunner()

    key = os.getenv("AUTOMATIC1_SSH_KEY")
    if key and Path(key).expanduser().is_file():
        return SSHRunner(
            user=os.getenv("AUTOMATIC1_SSH_USER", "root"),
            key_path=str(Path(key).expanduser()),
            passphrase=os.getenv("AUTOMATIC1_SSH_PASSPHRASE"),
            timeout=int(os.getenv("AUTOMATIC1_SSH_TIMEOUT", "300")),
        )
    return None
