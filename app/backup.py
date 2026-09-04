"""Backup/exportação do catálogo em JSON (feature 010).

Exporta setups + máquinas + execuções num snapshot portátil (meta + coleções).
Importação **aditiva/não destrutiva** (nome normalizado), reaplicando validações e
anti-segredo (FR-013/constituição IV). Execuções são vinculadas por `setup_nome`/
`maquina_nome` (ids novos no restore). Sem nova dependência.
"""
import json
from datetime import UTC, datetime

from sqlmodel import Session, select

from .config import settings
from .models import EnvironmentSetup, Execution, TargetHost
from .schemas import normalizar_nome, validar_campos, validar_maquina

FORMATO = "automatic1-catalogo"
VERSAO = 1

# Campos persistidos no snapshot (sem id/auditoria derivada).
_CAMPOS_SETUP = (
    "nome", "descricao", "plataforma_alvo", "origem_asset", "versao", "hash",
    "licenca", "status", "categoria", "dominio", "variaveis_deploy",
    "resultado_ultima_execucao",
)
_CAMPOS_MAQUINA = ("nome", "identificacao", "plataforma_alvo", "descricao", "status")
_CAMPOS_EXECUCAO = ("status", "resumo", "exit_code", "started_at", "finished_at")


class BackupError(Exception):
    """Erro estrutural de snapshot (formato/versão) — mensagem acionável."""


def _dt(valor: datetime | None) -> str | None:
    return valor.isoformat() if valor is not None else None


def _parse_dt(valor: str | None) -> datetime | None:
    if not valor:
        return None
    try:
        return datetime.fromisoformat(str(valor))
    except ValueError:
        return None


def _setup_para_json(s: EnvironmentSetup) -> dict:
    return {campo: (getattr(s, campo) or "") for campo in _CAMPOS_SETUP}


def _maquina_para_json(m: TargetHost) -> dict:
    return {campo: (getattr(m, campo) or "") for campo in _CAMPOS_MAQUINA}


def montar_snapshot(session: Session) -> dict:
    """Monta o snapshot completo (meta + setups + máquinas + execuções)."""
    setups = session.exec(select(EnvironmentSetup).order_by(EnvironmentSetup.nome)).all()
    maquinas = session.exec(select(TargetHost).order_by(TargetHost.nome)).all()
    execucoes = session.exec(select(Execution).order_by(Execution.id)).all()
    setups_por_id = {s.id: s for s in setups}
    maquinas_por_id = {m.id: m for m in maquinas}

    execucoes_json = []
    for e in execucoes:
        setup = setups_por_id.get(e.setup_id)
        maquina = maquinas_por_id.get(e.target_host_id)
        if setup is None or maquina is None:
            continue
        item = {campo: getattr(e, campo) for campo in _CAMPOS_EXECUCAO}
        item["setup_nome"] = setup.nome
        item["maquina_nome"] = maquina.nome
        item["criado_em"] = _dt(e.created_at)
        item["criado_por"] = e.created_by
        execucoes_json.append(item)

    return {
        "formato": FORMATO,
        "versao": VERSAO,
        "exportado_em": _dt(datetime.now(UTC)),
        "por": settings.operator_name,
        "setups": [_setup_para_json(s) for s in setups],
        "maquinas": [_maquina_para_json(m) for m in maquinas],
        "execucoes": execucoes_json,
    }


def _nome_existe(session: Session, modelo, nome: str) -> bool:
    alvo = normalizar_nome(nome)
    return any(normalizar_nome(r.nome) == alvo for r in session.exec(select(modelo)).all())


def importar_snapshot(session: Session, dados: dict, autor: str) -> dict:
    """Importa um snapshot de forma **aditiva**. Devolve relatório.

    ``dados`` já parseado de JSON. Erros estruturais (formato/versão) levantam
    ``BackupError``. Itens duplicados/inválidos são ignorados e contabilizados;
    execuções só entram quando o par setup×máquina existe após o import.
    """
    if dados.get("formato") != FORMATO or dados.get("versao") != VERSAO:
        raise BackupError(
            "Arquivo não é um snapshot do Automatic1 (formato/versão inválidos)."
        )

    relatorio = {
        "criados_setups": 0,
        "ignorados_setups": 0,
        "invalidos_setups": 0,
        "criadas_maquinas": 0,
        "ignoradas_maquinas": 0,
        "invalidas_maquinas": 0,
        "criadas_execucoes": 0,
        "ignoradas_execucoes": 0,
    }

    # --- Setups (aditivo por nome normalizado) --------------------------------
    for item in dados.get("setups") or []:
        dados_setup = {c: str(item.get(c, "") or "") for c in _CAMPOS_SETUP}
        if _nome_existe(session, EnvironmentSetup, dados_setup["nome"]):
            relatorio["ignorados_setups"] += 1
            continue
        erros = validar_campos(dados_setup)
        if erros:
            relatorio["invalidos_setups"] += 1
            continue
        session.add(
            EnvironmentSetup(
                **dados_setup,
                created_by=autor,
                updated_by=autor,
            )
        )
        relatorio["criados_setups"] += 1

    # --- Máquinas (aditivo por nome normalizado) ------------------------------
    for item in dados.get("maquinas") or []:
        dados_maquina = {c: str(item.get(c, "") or "") for c in _CAMPOS_MAQUINA}
        if _nome_existe(session, TargetHost, dados_maquina["nome"]):
            relatorio["ignoradas_maquinas"] += 1
            continue
        erros = validar_maquina(dados_maquina)
        if erros:
            relatorio["invalidas_maquinas"] += 1
            continue
        session.add(
            TargetHost(
                **dados_maquina,
                created_by=autor,
                updated_by=autor,
            )
        )
        relatorio["criadas_maquinas"] += 1

    session.flush()  # garante ids disponíveis p/ vínculo das execuções

    # --- Execuções (só quando setup×máquina existem; idempotente) -------------
    setups_por_nome = {
        normalizar_nome(s.nome): s.id
        for s in session.exec(select(EnvironmentSetup)).all()
    }
    maquinas_por_nome = {
        normalizar_nome(m.nome): m.id
        for m in session.exec(select(TargetHost)).all()
    }

    def _fingerprint(e: Execution) -> tuple:
        return (
            e.setup_id, e.target_host_id, e.status, e.resumo, e.exit_code,
            e.started_at, e.finished_at, e.created_at,
        )

    existentes = {
        _fingerprint(e)
        for e in session.exec(select(Execution)).all()
    }
    for item in dados.get("execucoes") or []:
        setup_id = setups_por_nome.get(normalizar_nome(str(item.get("setup_nome") or "")))
        maquina_id = maquinas_por_nome.get(normalizar_nome(str(item.get("maquina_nome") or "")))
        if setup_id is None or maquina_id is None:
            relatorio["ignoradas_execucoes"] += 1
            continue
        status = str(item.get("status") or "").strip()
        if status not in {"planejada", "em_andamento", "sucesso", "erro", "cancelada"}:
            relatorio["ignoradas_execucoes"] += 1
            continue
        resumo = str(item.get("resumo") or "").strip()
        criado_em = _parse_dt(item.get("criado_em")) or datetime.now(UTC)
        nova = Execution(
            setup_id=setup_id,
            target_host_id=maquina_id,
            status=status,
            resumo=resumo or None,
            exit_code=item.get("exit_code"),
            started_at=_parse_dt(item.get("started_at")),
            finished_at=_parse_dt(item.get("finished_at")),
            created_at=criado_em,
            created_by=autor,
        )
        if _fingerprint(nova) in existentes:
            relatorio["ignoradas_execucoes"] += 1
            continue
        session.add(nova)
        relatorio["criadas_execucoes"] += 1

    session.commit()
    return relatorio


def snapshot_para_json(snapshot: dict) -> str:
    """Serializa o snapshot em JSON UTF-8 (identado, sem segredos)."""
    return json.dumps(snapshot, ensure_ascii=False, indent=2, default=str)
