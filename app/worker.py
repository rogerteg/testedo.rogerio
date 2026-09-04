"""Worker de execução assíncrona do provisionador (feature 008).

Fila **em processo** (threads) — sem serviço externo no v1. O estado vive na
`Execution`: o disparo cria `em_andamento` e enfileira a conclusão; o worker
roda o runner e atualiza para `sucesso`/`erro`. Execuções órfãs (worker morto)
são recuperadas no startup (`recuperar_orfas`).
"""
import logging
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime

from sqlmodel import Session, select

from .database import engine
from .models import Execution
from .provisioner import ProvisionamentoError, concluir_execucao, redigir
from .runners import criar_runner

logger = logging.getLogger("automatic1_admin.worker")

_executor: ThreadPoolExecutor | None = None


def _get_executor() -> ThreadPoolExecutor:
    global _executor
    if _executor is None:
        _executor = ThreadPoolExecutor(
            max_workers=int(os.getenv("AUTOMATIC1_WORKERS", "2"))
        )
    return _executor


def provisionamento_assincrono() -> bool:
    """True = provisionamento em segundo plano (default); '0' força síncrono (testes)."""
    return os.getenv("AUTOMATIC1_ASYNC", "1") == "1"


def enfileirar(execucao_id: int) -> bool:
    """Enfileira a conclusão de uma `Execution`; devolve True se agendado."""
    try:
        _get_executor().submit(_trabalho, execucao_id)
        return True
    except RuntimeError:
        logger.exception("Falha ao enfileirar execução=%s", execucao_id)
        return False


def _trabalho(execucao_id: int) -> None:
    try:
        with Session(engine) as session:
            runner = criar_runner()
            if runner is None:
                _marcar_erro(session, execucao_id, "Credencial SSH não configurada ao concluir a execução.")
            else:
                concluir_execucao(session, runner, execucao_id)
    except ProvisionamentoError as exc:
        logger.warning("Execução %s não pôde ser concluída: %s", execucao_id, exc)
    except Exception:
        logger.exception("Erro inesperado ao concluir execução=%s", execucao_id)


def _marcar_erro(session: Session, execucao_id: int, motivo: str) -> None:
    execucao = session.get(Execution, execucao_id)
    if execucao is None or execucao.status != "em_andamento":
        return
    execucao.status = "erro"
    execucao.exit_code = None
    execucao.log = redigir(motivo, [])
    execucao.resumo = motivo[:1000]
    execucao.finished_at = datetime.now(UTC)
    session.add(execucao)
    session.commit()
    logger.warning("Execução %s marcada como erro: %s", execucao_id, motivo)


def _recuperar_orfas_em(session: Session) -> int:
    """Marca `em_andamento` órfãs como erro na sessão fornecida (testável)."""
    agora = datetime.now(UTC)
    count = 0
    orfas = session.exec(select(Execution).where(Execution.status == "em_andamento")).all()
    for execucao in orfas:
        execucao.status = "erro"
        execucao.exit_code = None
        motivo = "Execução interrompida por reinício do serviço."
        execucao.log = f"{execucao.log}\n{motivo}".strip() if execucao.log else motivo
        execucao.resumo = motivo[:1000]
        execucao.finished_at = agora
        session.add(execucao)
        count += 1
    if count:
        session.commit()
    return count


def recuperar_orfas() -> int:
    """Recupera execuções órfãs no banco real (startup) — FR-004 (008)."""
    with Session(engine) as session:
        count = _recuperar_orfas_em(session)
    if count:
        logger.warning("Recuperadas %s execução(ões) órfã(s) no startup.", count)
    return count
