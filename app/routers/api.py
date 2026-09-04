"""API REST de leitura do Automatic1 Admin (feature 006 — Q2=A).

Somente leitura, autenticada por token (`Authorization: Bearer <token>`).
Respostas JSON sem segredos.
"""
from typing import Annotated

from fastapi import APIRouter, Body, Depends, Header, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlmodel import Session, select

from ..auth import token_api_valido, token_escrita_valido
from ..config import settings
from ..database import get_session
from ..models import PLATAFORMA_PADRAO, EnvironmentSetup, Execution, TargetHost
from ..schemas import (
    CATEGORIA_VALIDOS,
    normalizar_nome,
    validar_campos,
    validar_execucao,
    validar_maquina,
)

router = APIRouter(prefix="/api")


def _dt(valor):
    return valor.isoformat() if valor is not None else None


def exigir_token(authorization: Annotated[str | None, Header()] = None) -> None:
    token = ""
    if authorization and authorization.startswith("Bearer "):
        token = authorization[len("Bearer "):].strip()
    if not token_api_valido(token):
        raise HTTPException(status_code=401, detail="Não autorizado.")


def _setup_para_json(s: EnvironmentSetup) -> dict:
    return {
        "id": s.id,
        "nome": s.nome,
        "descricao": s.descricao,
        "plataforma_alvo": s.plataforma_alvo,
        "origem_asset": s.origem_asset,
        "versao": s.versao,
        "hash": s.hash,
        "licenca": s.licenca,
        "categoria": s.categoria,
        "dominio": s.dominio,
        "variaveis_deploy": s.variaveis_deploy,
        "status": s.status,
        "atualizado_em": _dt(s.updated_at),
    }


def _maquina_para_json(m: TargetHost) -> dict:
    return {
        "id": m.id,
        "nome": m.nome,
        "identificacao": m.identificacao,
        "plataforma_alvo": m.plataforma_alvo,
        "descricao": m.descricao,
        "status": m.status,
        "atualizado_em": _dt(m.updated_at),
    }


def _execucao_para_json(e: Execution) -> dict:
    return {
        "id": e.id,
        "setup_id": e.setup_id,
        "maquina_id": e.target_host_id,
        "status": e.status,
        "resumo": e.resumo,
        "exit_code": e.exit_code,
        "criado_em": _dt(e.created_at),
        "criado_por": e.created_by,
    }


@router.get("/setups", dependencies=[Depends(exigir_token)])
def api_setups(
    session: Session = Depends(get_session),
    q: Annotated[str, Query()] = "",
    categoria: Annotated[str, Query()] = "",
) -> dict:
    termo = q.strip().lower()
    registros = session.exec(
        select(EnvironmentSetup).where(EnvironmentSetup.status != "arquivado")
    ).all()
    if termo:
        registros = [
            r for r in registros
            if termo in r.nome.lower() or termo in r.plataforma_alvo.lower()
        ]
    if categoria:
        registros = [r for r in registros if r.categoria == categoria]
    itens = [_setup_para_json(r) for r in registros]
    return {"itens": itens, "total": len(itens)}


@router.get("/maquinas", dependencies=[Depends(exigir_token)])
def api_maquinas(
    session: Session = Depends(get_session),
    q: Annotated[str, Query()] = "",
) -> dict:
    termo = q.strip().lower()
    registros = session.exec(select(TargetHost)).all()
    if termo:
        registros = [
            m for m in registros
            if termo in m.nome.lower() or termo in m.identificacao.lower()
        ]
    itens = [_maquina_para_json(m) for m in registros]
    return {"itens": itens, "total": len(itens)}


@router.get("/execucoes", dependencies=[Depends(exigir_token)])
def api_execucoes(
    session: Session = Depends(get_session),
    setup_id: Annotated[int | None, Query()] = None,
    maquina_id: Annotated[int | None, Query()] = None,
) -> dict:
    stmt = select(Execution)
    if setup_id is not None:
        stmt = stmt.where(Execution.setup_id == setup_id)
    if maquina_id is not None:
        stmt = stmt.where(Execution.target_host_id == maquina_id)
    registros = session.exec(stmt.order_by(Execution.created_at.desc())).all()
    itens = [_execucao_para_json(e) for e in registros]
    return {"itens": itens, "total": len(itens)}


# ---------------------------------------------------------------------------
# Feature 007 — Escrita via API (token de escrita)
# ---------------------------------------------------------------------------

_CHAVES_SETUP = (
    "nome", "descricao", "plataforma_alvo", "origem_asset",
    "versao", "hash", "licenca", "status", "categoria",
    "dominio", "variaveis_deploy",
)
_CHAVES_MAQUINA = ("nome", "identificacao", "plataforma_alvo", "descricao")


def _extrair_bearer(authorization: str | None) -> str:
    if authorization and authorization.startswith("Bearer "):
        return authorization[len("Bearer "):].strip()
    return ""


def exigir_token_escrita(authorization: Annotated[str | None, Header()] = None) -> None:
    token = _extrair_bearer(authorization)
    if token_escrita_valido(token):
        return
    if token_api_valido(token):
        raise HTTPException(status_code=403, detail={"erros": {"auth": "Token de leitura não permite escrita."}})
    raise HTTPException(status_code=401, detail={"erros": {"auth": "Não autorizado."}})


def _payload_para_dados(payload: dict, chaves: tuple) -> dict:
    return {
        chave: str(payload.get(chave, "")).strip() if payload.get(chave) is not None else ""
        for chave in chaves
    }


def _setup_duplicado(session: Session, nome: str) -> bool:
    alvo = normalizar_nome(nome)
    return any(normalizar_nome(s.nome) == alvo for s in session.exec(select(EnvironmentSetup)).all())


def _maquina_duplicada(session: Session, nome: str) -> bool:
    alvo = normalizar_nome(nome)
    return any(normalizar_nome(m.nome) == alvo for m in session.exec(select(TargetHost)).all())


@router.post("/setups", dependencies=[Depends(exigir_token_escrita)])
def criar_setup_api(
    payload: Annotated[dict, Body()],
    session: Session = Depends(get_session),
) -> JSONResponse:
    dados = _payload_para_dados(payload, _CHAVES_SETUP)
    erros = validar_campos(dados)
    categoria = dados.get("categoria") or ""
    if categoria and categoria not in CATEGORIA_VALIDOS:
        erros["categoria"] = "Categoria inválida."
    if not erros and _setup_duplicado(session, dados["nome"]):
        raise HTTPException(status_code=409, detail={"erros": {"nome": "Já existe um setup com esse nome."}})
    if erros:
        raise HTTPException(status_code=422, detail={"erros": erros})

    setup = EnvironmentSetup(
        **{k: v for k, v in dados.items()},
        created_by=settings.operator_name,
        updated_by=settings.operator_name,
    )
    session.add(setup)
    session.commit()
    session.refresh(setup)
    return JSONResponse(status_code=201, content=_setup_para_json(setup))


@router.post("/maquinas", dependencies=[Depends(exigir_token_escrita)])
def criar_maquina_api(
    payload: Annotated[dict, Body()],
    session: Session = Depends(get_session),
) -> JSONResponse:
    dados = _payload_para_dados(payload, _CHAVES_MAQUINA)
    if not dados["plataforma_alvo"]:
        dados["plataforma_alvo"] = PLATAFORMA_PADRAO
    erros = validar_maquina(dados)
    if not erros and _maquina_duplicada(session, dados["nome"]):
        raise HTTPException(status_code=409, detail={"erros": {"nome": "Já existe uma máquina com esse nome."}})
    if erros:
        raise HTTPException(status_code=422, detail={"erros": erros})

    maquina = TargetHost(
        **{k: v for k, v in dados.items()},
        created_by=settings.operator_name,
        updated_by=settings.operator_name,
    )
    session.add(maquina)
    session.commit()
    session.refresh(maquina)
    return JSONResponse(status_code=201, content=_maquina_para_json(maquina))


@router.post("/execucoes", dependencies=[Depends(exigir_token_escrita)])
def registrar_execucao_api(
    payload: Annotated[dict, Body()],
    session: Session = Depends(get_session),
) -> JSONResponse:
    dados = _payload_para_dados(payload, ("setup_id", "target_host_id", "status", "resumo"))
    try:
        sid = int(dados["setup_id"]) if dados["setup_id"] else None
        hid = int(dados["target_host_id"]) if dados["target_host_id"] else None
    except ValueError:
        sid = None
        hid = None

    if sid is None:
        raise HTTPException(status_code=422, detail={"erros": {"setup_id": "O setup_id é obrigatório."}})
    if session.get(EnvironmentSetup, sid) is None:
        raise HTTPException(status_code=404, detail={"erros": {"setup_id": "Setup não encontrado."}})
    if hid is None:
        raise HTTPException(status_code=422, detail={"erros": {"target_host_id": "A máquina é obrigatória."}})
    host = session.get(TargetHost, hid)
    if host is None:
        raise HTTPException(status_code=404, detail={"erros": {"target_host_id": "Máquina não encontrada."}})
    if host.status != "ativa":
        raise HTTPException(status_code=400, detail={"erros": {"target_host_id": "A máquina selecionada está inativa."}})

    erros = validar_execucao({"status": dados["status"], "resumo": dados["resumo"]})
    if erros:
        raise HTTPException(status_code=422, detail={"erros": erros})

    execucao = Execution(
        setup_id=sid,
        target_host_id=hid,
        status=dados["status"],
        resumo=dados["resumo"] or None,
        created_by=settings.operator_name,
    )
    session.add(execucao)
    session.commit()
    session.refresh(execucao)
    return JSONResponse(status_code=201, content=_execucao_para_json(execucao))


def _execucao_detalhe_json(e: Execution) -> dict:
    dados = _execucao_para_json(e)
    dados["log"] = e.log
    dados["iniciado_em"] = _dt(e.started_at)
    dados["finalizado_em"] = _dt(e.finished_at)
    return dados


@router.get("/execucoes/{execucao_id}", dependencies=[Depends(exigir_token)])
def api_execucao_detalhe(
    execucao_id: int,
    session: Session = Depends(get_session),
) -> dict:
    """Detalhe de uma execução (inclusive log sanitizado) — p/ polling (feature 008)."""
    execucao = session.get(Execution, execucao_id)
    if execucao is None:
        raise HTTPException(status_code=404, detail={"erros": {"execucao_id": "Execução não encontrada."}})
    return _execucao_detalhe_json(execucao)


# ---------------------------------------------------------------------------
# Feature 011 — Monitoramento/status dos serviços (leitura)
# ---------------------------------------------------------------------------

@router.get("/maquinas/{maquina_id}/status", dependencies=[Depends(exigir_token)])
def api_maquina_status(
    maquina_id: int,
    session: Session = Depends(get_session),
) -> dict:
    """Consulta o status da stack da máquina (somente leitura) — feature 011.

    Retorna ``{"status": "sucesso"|"erro", "saida": ..., "exit_code": ...}``.
    Erros acionáveis: máquina inativa (400) / não encontrada (404) / sem runner (503).
    """
    from ..monitor import consultar_status
    from ..runners import criar_runner

    maquina = session.get(TargetHost, maquina_id)
    if maquina is None:
        raise HTTPException(status_code=404, detail={"erros": {"maquina_id": "Máquina não encontrada."}})
    if maquina.status != "ativa":
        raise HTTPException(
            status_code=400,
            detail={"erros": {"maquina_id": "A máquina está inativa. Reative-a para consultar o status."}},
        )

    runner = criar_runner()
    if runner is None:
        raise HTTPException(
            status_code=503,
            detail={"erros": {"runner": "Credencial SSH não configurada (AUTOMATIC1_SSH_KEY)."}},
        )

    resultado = consultar_status(runner, host=maquina.identificacao)
    return {
        "status": "sucesso" if resultado["ok"] else "erro",
        "saida": resultado["saida"],
        "exit_code": resultado["exit_code"],
    }
