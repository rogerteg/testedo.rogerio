"""Engine do provisionador real (feature 004).

Orquestra a execução de um setup numa máquina alvo: guardas (estado/host/
concorrência/origem), montagem do comando idempotente (download + verificação
sha256 quando há hash + execução via bash), redação de segredos e gravação da
`Execution` (feature 003) com status real, log, exit_code e horários.
Sem credenciais persistidas (constituição IV) — vêm do ambiente/runner.
"""
import logging
import os
import re
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlmodel import Session, select

from .models import Execution

if TYPE_CHECKING:  # evita import circular pesado p/ type-check
    from .models import EnvironmentSetup, TargetHost
    from .runners import Runner

logger = logging.getLogger("automatic1_admin.provisioner")


class ProvisionamentoError(Exception):
    """Guarda de provisionamento violada — mensagem acionável, sem efeito colateral."""


def _agora() -> datetime:
    return datetime.now(UTC)


def _eh_origem_executavel(origem: str | None) -> bool:
    """Origem executável no v1 = script `.sh` acessível por HTTP(S) (Q3=A)."""
    origem = (origem or "").strip().lower()
    return origem.startswith(("http://", "https://")) and origem.endswith(".sh")


def montar_comando(setup: "EnvironmentSetup") -> str:
    """Monta o comando idempotente executado no host (feature 004).

    Baixa o asset de ``origem_asset``, verifica sha256 quando ``hash`` presente
    (divergência aborta antes de executar) e roda via ``bash``. Sempre limpa o
    diretório temporário e propaga o código de saída.
    """
    origem = setup.origem_asset.strip()
    partes = [
        "tmpd=$(mktemp -d)",
        f"curl -fsSL '{origem}' -o \"$tmpd/asset\" || {{ echo 'ERRO: falha no download do asset'; rm -rf \"$tmpd\"; exit 1; }}",
    ]
    if setup.hash:
        partes.append(
            f"echo '{setup.hash}  $tmpd/asset' | sha256sum -c - >/dev/null 2>&1 "
            "|| { echo 'ERRO: hash diverge do esperado — execução bloqueada'; rm -rf \"$tmpd\"; exit 2; }"
        )
    partes.append('bash "$tmpd/asset"; rc=$?; rm -rf "$tmpd"; exit $rc')
    return "; ".join(partes)


_PADRAO_SEGREDO = re.compile(
    r"(?i)(\b(?:token|secret|senha|password|passwd|apikey|api_key|access_key|credential|chave)"
    r"(?:\s*[:=]\s*|['\"]?\s*[:=]\s*)?)([^\s;,'\"]+)"
)


def redigir(texto: str | None, segredos: list[str] | None = None) -> str:
    """Remove segredos de um texto (FR-005): valores conhecidos + padrões chave=valor."""
    if not texto:
        return texto or ""
    limpo = texto
    for valor in segredos or []:
        if valor:
            limpo = limpo.replace(str(valor), "[REDACTED]")

    def _mascarar(m: re.Match) -> str:
        return f"{m.group(1)}[REDACTED]"

    return _PADRAO_SEGREDO.sub(_mascarar, limpo)


def _segredos_do_ambiente() -> list[str]:
    return [v for v in [os.getenv("AUTOMATIC1_SSH_PASSPHRASE")] if v]


def _tem_execucao_em_andamento(session: Session, setup_id: int, target_host_id: int) -> bool:
    stmt = select(Execution).where(
        Execution.setup_id == setup_id,
        Execution.target_host_id == target_host_id,
        Execution.status == "em_andamento",
    )
    return session.exec(stmt).first() is not None


def _primeira_linha(texto: str, limite: int = 1000) -> str:
    linha = texto.strip().splitlines()[0] if texto.strip() else ""
    return linha[:limite]


def provisionar(
    session: Session,
    runner: "Runner",
    setup: "EnvironmentSetup",
    host: "TargetHost",
    autor: str,
) -> Execution:
    """Executa um setup numa máquina alvo e grava a `Execution` real (feature 004).

    Guardas violadas levantam ``ProvisionamentoError`` **sem criar** `Execution`.
    """
    # Guardas (FR-002/FR-007/FR-003) — sem efeito colateral.
    if setup.status == "arquivado":
        raise ProvisionamentoError("O setup está arquivado e não pode ser provisionado.")
    if host.status != "ativa":
        raise ProvisionamentoError("A máquina alvo está inativa. Reative-a para provisionar.")
    if not _eh_origem_executavel(setup.origem_asset):
        raise ProvisionamentoError(
            "origem_asset não é um artefato executável (.sh). Informe o script instalador "
            "(scripts por ferramenta chegam com a feature instalador)."
        )
    if _tem_execucao_em_andamento(session, setup.id, host.id):
        raise ProvisionamentoError(
            "Já existe uma execução em andamento para este setup nesta máquina. Aguarde concluir."
        )

    timeout = int(os.getenv("AUTOMATIC1_SSH_TIMEOUT", "300"))
    comando = montar_comando(setup)

    execucao = Execution(
        setup_id=setup.id,
        target_host_id=host.id,
        status="em_andamento",
        created_by=autor,
        started_at=_agora(),
    )
    session.add(execucao)
    session.commit()
    session.refresh(execucao)

    try:
        resultado = runner.executar(comando=comando, host=host.identificacao, timeout=timeout)
    except Exception as exc:
        logger.exception("Falha de transporte ao provisionar setup=%s host=%s", setup.id, host.id)
        saida = redigir(f"ERRO no transporte SSH: {exc}", _segredos_do_ambiente())
        execucao.status = "erro"
        execucao.exit_code = None
        execucao.log = saida
        execucao.resumo = _primeira_linha(saida)
        execucao.finished_at = _agora()
        session.add(execucao)
        session.commit()
        return execucao

    saida = redigir(resultado.output, _segredos_do_ambiente())
    execucao.status = "sucesso" if resultado.exit_code == 0 else "erro"
    execucao.exit_code = resultado.exit_code
    execucao.log = saida
    execucao.resumo = _primeira_linha(saida)
    execucao.finished_at = _agora()
    session.add(execucao)
    session.commit()
    logger.info(
        "Provisionamento concluído setup=%s host=%s status=%s exit=%s por %s",
        setup.id,
        host.id,
        execucao.status,
        execucao.exit_code,
        autor,
    )
    return execucao


def avaliar(setup: "EnvironmentSetup", host: "TargetHost | None", runner: "Runner | None") -> dict:
    """Avalia a prontidão para provisionar (para exibição antes do POST).

    Retorna ``{"ok": bool, "erros": list[str], "avisos": list[str]}``.
    """
    erros: list[str] = []
    avisos: list[str] = []

    if setup.status == "arquivado":
        erros.append("O setup está arquivado e não pode ser provisionado.")
    if host is not None and host.status != "ativa":
        erros.append("A máquina alvo está inativa. Reative-a para provisionar.")
    if not _eh_origem_executavel(setup.origem_asset):
        erros.append(
            "origem_asset não é um artefato executável (.sh). Informe o script instalador "
            "(scripts por ferramenta chegam com a feature instalador)."
        )
    if runner is None:
        erros.append(
            "Credencial SSH não configurada no ambiente. Defina AUTOMATIC1_SSH_KEY "
            "(e opcionalmente AUTOMATIC1_SSH_USER)."
        )
    if setup.hash is None and not erros:
        avisos.append("Sem hash registrado — a integridade do asset não será verificada nesta execução.")

    return {"ok": not erros, "erros": erros, "avisos": avisos}
