"""API REST de leitura do Automatic1 Admin (feature 006 — Q2=A).

Somente leitura, autenticada por token (`Authorization: Bearer <token>`).
Respostas JSON sem segredos.
"""
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlmodel import Session, select

from ..auth import token_api_valido
from ..database import get_session
from ..models import EnvironmentSetup, Execution, TargetHost

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
