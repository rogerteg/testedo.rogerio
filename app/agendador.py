"""Agendador de rotinas cron (feature 012).

Parser **caseiro** de expressões cron de 5 campos (``minuto hora dia mês
dia-semana``) com suporte a ``*``, ``*/passo`` e listas ``a,b`` — sem dependência
nova (revisão supply-chain / constituição). ``executar_vencidos`` reusa as guardas
do provisionador (004) e o worker assíncrono (008). ``iniciar_rotina`` dispara uma
thread daemon que verifica os vencidos periodicamente (rotina interna).
"""
import logging
import os
import threading
import time
from datetime import UTC, datetime

from sqlmodel import Session, select

from .models import Agendamento, EnvironmentSetup, TargetHost
from .provisioner import ProvisionamentoError, concluir_execucao, iniciar_execucao
from .runners import criar_runner
from .worker import enfileirar, provisionamento_assincrono

logger = logging.getLogger("automatic1_admin.agendador")

INTERVALO_PADRAO_SEG = 60

# (min, max) por campo — ordem: minuto hora dia mês dia-semana.
_CAMPOS = (
    ("minuto", 0, 59),
    ("hora", 0, 23),
    ("dia", 1, 31),
    ("mês", 1, 12),
    ("dia_semana", 0, 6),
)


class CronInvalido(ValueError):
    """Expressão cron inválida — mensagem acionável."""


def _interpretar(campo: str, minimo: int, maximo: int) -> set[int]:
    """Interpreta um campo cron: ``*``, ``*/passo``, listas ``a,b``, número."""
    valores: set[int] = set()
    for parte in campo.split(","):
        parte = parte.strip()
        if not parte:
            raise CronInvalido("campo vazio.")
        passo: int | None = None
        if "/" in parte:
            base, _, passo_txt = parte.partition("/")
            try:
                passo = int(passo_txt)
            except ValueError as exc:
                raise CronInvalido(f"passo inválido: {passo_txt!r}.") from exc
            if passo <= 0:
                raise CronInvalido("passo deve ser > 0.")
            parte = base
        if parte == "*":
            inicio, fim = minimo, maximo
        else:
            try:
                inicio = fim = int(parte)
            except ValueError as exc:
                raise CronInvalido(f"valor inválido: {parte!r}.") from exc
            if not (minimo <= inicio <= maximo):
                raise CronInvalido(f"valor {inicio} fora do intervalo {minimo}-{maximo}.")
        if passo is None:
            valores.update(range(inicio, fim + 1))
        else:
            valores.update(range(inicio, maximo + 1, passo))
    return valores


def _parsear(expressao: str) -> list[set[int]]:
    partes = expressao.strip().split()
    if len(partes) != 5:
        raise CronInvalido("A expressão deve ter 5 campos (minuto hora dia mês dia-semana).")
    return [_interpretar(p, lo, hi) for p, (_, lo, hi) in zip(partes, _CAMPOS)]


def validar_cron(expressao: str) -> str | None:
    """Valida a expressão cron; devolve mensagem de erro ou ``None`` (válida)."""
    if not expressao or not expressao.strip():
        return "A expressão cron é obrigatória (5 campos: minuto hora dia mês dia-semana)."
    try:
        _parsear(expressao)
    except CronInvalido as exc:
        return f"Expressão cron inválida: {exc}"
    return None


def expressao_casa(expressao: str, agora: datetime) -> bool:
    """True se a expressão casa no instante ``agora`` (5 campos, local/UTC)."""
    try:
        minuto, hora, dia, mes, dia_semana = _parsear(expressao)
    except CronInvalido:
        return False
    # Cron: 0=domingo ... 6=sábado. Python weekday(): 0=segunda ... 6=domingo.
    dias_cron_para_python = {(d + 6) % 7 for d in dia_semana}
    return (
        agora.minute in minuto
        and agora.hour in hora
        and agora.day in dia
        and agora.month in mes
        and agora.weekday() in dias_cron_para_python
    )


def _para_utc(valor: datetime) -> datetime:
    """Normaliza p/ UTC (SQLite devolve datetime naive ao reler)."""
    if valor.tzinfo is None:
        return valor.replace(tzinfo=UTC)
    return valor.astimezone(UTC)


def vencidos_em(session: Session, agora: datetime | None = None) -> list[Agendamento]:
    """Agendamentos **ativos** cuja expressão casa no minuto atual e ainda não
    dispararam neste minuto (``ultimo_disparo`` fora da janela)."""
    agora = agora or datetime.now(UTC)
    inicio_minuto = agora.replace(second=0, microsecond=0)

    vencidos: list[Agendamento] = []
    ativos = session.exec(select(Agendamento).where(Agendamento.ativo == True)).all()
    for ag in ativos:
        ultimo = _para_utc(ag.ultimo_disparo) if ag.ultimo_disparo is not None else None
        if ultimo is not None and ultimo >= inicio_minuto:
            continue  # já disparou nesta janela (evita duplicação)
        if expressao_casa(ag.cron, agora):
            vencidos.append(ag)
    return vencidos


def executar_vencidos(session: Session, autor: str, agora: datetime | None = None) -> int:
    """Dispara os agendamentos vencidos (1×/janela), reusando guardas 004 e worker 008.

    Retorna quantos disparos foram iniciados. Guardas violadas (setup arquivado,
    máquina inativa, par em andamento, origem não executável) apenas pulam o
    agendamento (registrado no log) — sem criar `Execution`.
    """
    disparados = 0
    agora = agora or datetime.now(UTC)

    for ag in vencidos_em(session, agora):
        setup = session.get(EnvironmentSetup, ag.setup_id)
        host = session.get(TargetHost, ag.target_host_id)
        if setup is None or host is None:
            ag.ativo = False  # vínculo quebrado → desativa p/ não repetir
            session.add(ag)
            session.commit()
            continue
        try:
            execucao = iniciar_execucao(session, setup, host, autor=autor)
        except ProvisionamentoError as exc:
            logger.warning(
                "Agendamento %s bloqueado (setup=%s máquina=%s): %s",
                ag.id, ag.setup_id, ag.target_host_id, exc,
            )
            continue

        if provisionamento_assincrono():
            enfileirar(execucao.id)
        else:
            runner = criar_runner()
            if runner is not None:
                concluir_execucao(session, runner, execucao.id)
            else:
                execucao.status = "erro"
                execucao.exit_code = None
                execucao.log = "Runner não configurado (AUTOMATIC1_SSH_KEY) para conclusão síncrona."
                execucao.resumo = execucao.log[:1000]
                execucao.finished_at = agora
                session.add(execucao)
                session.commit()

        ag.ultimo_disparo = agora
        ag.updated_at = agora
        session.add(ag)
        session.commit()
        disparados += 1

    return disparados


def _loop_rotina() -> None:
    intervalo = int(os.getenv("AUTOMATIC1_SCHEDULER_INTERVALO", str(INTERVALO_PADRAO_SEG)))
    while True:
        try:
            from .config import settings
            from .database import engine

            with Session(engine) as session:
                disparados = executar_vencidos(session, autor=settings.operator_name)
                if disparados:
                    logger.info("Rotina: %s disparo(s) de agendamentos vencidos.", disparados)
        except Exception:
            logger.exception("Erro na verificação de agendamentos (rotina).")
        time.sleep(max(intervalo, 5))


def iniciar_rotina() -> threading.Thread:
    """Inicia a thread daemon de rotina (intervalo configurável)."""
    thread = threading.Thread(
        target=_loop_rotina,
        name="automatic1-rotina",
        daemon=True,
    )
    thread.start()
    logger.info("Rotina de agendamentos iniciada (intervalo %ss).", INTERVALO_PADRAO_SEG)
    return thread