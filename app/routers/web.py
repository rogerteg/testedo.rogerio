"""Rotas web (páginas) do Automatic1 Admin — CRUD de setups.

Fase atual (v1): US1 (cadastrar) e US2 (listar) — P1.
Slices futuras (US3-US5) adicionam detalhe/edição/arquivamento aqui.
"""
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from ..config import settings
from ..database import get_session
from ..models import EnvironmentSetup
from ..schemas import STATUS_LABEL, normalizar_nome, validar_campos

router = APIRouter()
templates = Jinja2Templates(
    directory=str(Path(__file__).resolve().parents[1] / "templates")
)
logger = logging.getLogger("automatic1_admin.web")

CAMPOS = [
    "nome",
    "descricao",
    "plataforma_alvo",
    "origem_asset",
    "versao",
    "hash",
    "licenca",
    "status",
    "resultado_ultima_execucao",
]

STATUS_OPCOES = [
    ("rascunho", "Rascunho"),
    ("ativo", "Ativo"),
    ("com_erro", "Com erro"),
    ("arquivado", "Arquivado"),
]


@router.get("/healthz", response_class=HTMLResponse)
def healthz() -> HTMLResponse:
    return HTMLResponse("ok")


def _dados_vazios() -> dict:
    return {campo: "" for campo in CAMPOS}


def _existe_nome_duplicado(session: Session, nome: str, excluir_id: int | None = None) -> bool:
    """Verifica unicidade de nome (case/whitespace-insensitive — FR-002)."""
    alvo = normalizar_nome(nome)
    registros = session.exec(select(EnvironmentSetup)).all()
    for reg in registros:
        if excluir_id is not None and reg.id == excluir_id:
            continue
        if normalizar_nome(reg.nome) == alvo:
            return True
    return False


def _obter_setup(session: Session, setup_id: int) -> EnvironmentSetup:
    """Busca um setup pelo id ou levanta 404 (amigável)."""
    setup = session.get(EnvironmentSetup, setup_id)
    if setup is None:
        raise HTTPException(status_code=404, detail="Setup não encontrado.")
    return setup


def _agora() -> datetime:
    return datetime.now(UTC)


# ---------------------------------------------------------------------------
# US1 — Cadastrar (GET /setups/novo + POST /setups)
# ---------------------------------------------------------------------------

@router.get("/setups/novo")
def novo_setup(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "setups/form.html",
        {
            "title": "Novo setup de ambiente",
            "acao": "/setups",
            "dados": _dados_vazios(),
            "erros": {},
            "status_opcoes": STATUS_OPCOES,
            "status_label": STATUS_LABEL,
            "mensagem": None,
        },
    )


@router.post("/setups")
def criar_setup(
    request: Request,
    session: Session = Depends(get_session),
    nome: Annotated[str, Form()] = "",
    descricao: Annotated[str, Form()] = "",
    plataforma_alvo: Annotated[str, Form()] = "",
    origem_asset: Annotated[str, Form()] = "",
    versao: Annotated[str, Form()] = "",
    hash: Annotated[str, Form()] = "",
    licenca: Annotated[str, Form()] = "",
    status: Annotated[str, Form()] = "rascunho",
    resultado_ultima_execucao: Annotated[str, Form()] = "",
) -> HTMLResponse:
    dados = {
        "nome": nome.strip(),
        "descricao": descricao.strip(),
        "plataforma_alvo": plataforma_alvo.strip(),
        "origem_asset": origem_asset.strip(),
        "versao": versao.strip(),
        "hash": hash.strip(),
        "licenca": licenca.strip(),
        "status": status.strip() or "rascunho",
        "resultado_ultima_execucao": resultado_ultima_execucao.strip(),
    }

    erros = validar_campos(dados)
    if not erros and _existe_nome_duplicado(session, dados["nome"]):
        erros["nome"] = "Já existe um setup com esse nome."

    if erros:
        # FR-004: erros por campo, dados preservados, nada persistido (re-render 200).
        return templates.TemplateResponse(
            request,
            "setups/form.html",
            {
                "title": "Novo setup de ambiente",
                "acao": "/setups",
                "dados": dados,
                "erros": erros,
                "status_opcoes": STATUS_OPCOES,
                "status_label": STATUS_LABEL,
                "mensagem": {"tipo": "error", "texto": "Corrija os campos destacados e tente novamente."},
            },
        )

    setup = EnvironmentSetup(
        **dados,
        created_by=settings.operator_name,
        updated_by=settings.operator_name,
    )
    session.add(setup)
    session.commit()
    session.refresh(setup)
    logger.info("Setup criado id=%s nome=%r por %s", setup.id, setup.nome, settings.operator_name)

    return RedirectResponse(url="/setups?sucesso=registro_criado", status_code=303)


# ---------------------------------------------------------------------------
# US2 — Listar (GET /setups)
# ---------------------------------------------------------------------------

@router.get("/setups")
def listar_setups(
    request: Request,
    session: Session = Depends(get_session),
    q: Annotated[str, Query()] = "",
    sucesso: Annotated[str, Query()] = "",
) -> HTMLResponse:
    termo = q.strip()
    statement = select(EnvironmentSetup).where(EnvironmentSetup.status != "arquivado")

    registros = session.exec(statement).all()
    if termo:
        filtro = termo.lower()
        registros = [
            r
            for r in registros
            if filtro in r.nome.lower() or filtro in r.plataforma_alvo.lower()
        ]

    registros.sort(key=lambda r: r.updated_at, reverse=True)

    mensagem = None
    if sucesso == "registro_criado":
        mensagem = {"tipo": "success", "texto": "Setup cadastrado com sucesso."}
    elif sucesso == "registro_arquivado":
        mensagem = {"tipo": "success", "texto": "Setup arquivado com sucesso."}

    return templates.TemplateResponse(
        request,
        "setups/list.html",
        {
            "title": "Setups de ambiente",
            "setups": registros,
            "termo": termo,
            "status_label": STATUS_LABEL,
            "mensagem": mensagem,
        },
    )


# ---------------------------------------------------------------------------
# US3 — Visualizar detalhes (GET /setups/{id})
# ---------------------------------------------------------------------------

@router.get("/setups/{setup_id}")
def detalhe_setup(
    request: Request,
    setup_id: int,
    session: Session = Depends(get_session),
    sucesso: str = Query(""),
) -> HTMLResponse:
    setup = _obter_setup(session, setup_id)

    mensagem = None
    if sucesso == "registro_atualizado":
        mensagem = {"tipo": "success", "texto": "Setup atualizado com sucesso."}

    return templates.TemplateResponse(
        request,
        "setups/detail.html",
        {
            "title": setup.nome,
            "setup": setup,
            "status_label": STATUS_LABEL,
            "mensagem": mensagem,
        },
    )


# ---------------------------------------------------------------------------
# US4 — Editar (GET/POST /setups/{id}/editar)
# ---------------------------------------------------------------------------

@router.get("/setups/{setup_id}/editar")
def editar_form(
    request: Request,
    setup_id: int,
    session: Session = Depends(get_session),
) -> HTMLResponse:
    setup = _obter_setup(session, setup_id)
    dados = {campo: (getattr(setup, campo) or "") for campo in CAMPOS}
    return templates.TemplateResponse(
        request,
        "setups/form.html",
        {
            "title": f"Editar: {setup.nome}",
            "acao": f"/setups/{setup_id}/editar",
            "dados": dados,
            "erros": {},
            "botao": "Salvar alterações",
            "status_opcoes": STATUS_OPCOES,
            "status_label": STATUS_LABEL,
            "mensagem": None,
        },
    )


@router.post("/setups/{setup_id}/editar")
def editar_setup(
    request: Request,
    setup_id: int,
    session: Session = Depends(get_session),
    nome: Annotated[str, Form()] = "",
    descricao: Annotated[str, Form()] = "",
    plataforma_alvo: Annotated[str, Form()] = "",
    origem_asset: Annotated[str, Form()] = "",
    versao: Annotated[str, Form()] = "",
    hash: Annotated[str, Form()] = "",
    licenca: Annotated[str, Form()] = "",
    status: Annotated[str, Form()] = "rascunho",
    resultado_ultima_execucao: Annotated[str, Form()] = "",
) -> HTMLResponse:
    setup = _obter_setup(session, setup_id)

    dados = {
        "nome": nome.strip(),
        "descricao": descricao.strip(),
        "plataforma_alvo": plataforma_alvo.strip(),
        "origem_asset": origem_asset.strip(),
        "versao": versao.strip(),
        "hash": hash.strip(),
        "licenca": licenca.strip(),
        "status": status.strip() or "rascunho",
        "resultado_ultima_execucao": resultado_ultima_execucao.strip(),
    }

    erros = validar_campos(dados)
    if not erros and _existe_nome_duplicado(session, dados["nome"], excluir_id=setup.id):
        erros["nome"] = "Já existe um setup com esse nome."

    if erros:
        # FR-004/FR-009: erros por campo, sem atualização parcial.
        return templates.TemplateResponse(
            request,
            "setups/form.html",
            {
                "title": f"Editar: {setup.nome}",
                "acao": f"/setups/{setup_id}/editar",
                "dados": dados,
                "erros": erros,
                "botao": "Salvar alterações",
                "status_opcoes": STATUS_OPCOES,
                "status_label": STATUS_LABEL,
                "mensagem": {"tipo": "error", "texto": "Corrija os campos destacados e tente novamente."},
            },
        )

    for campo, valor in dados.items():
        setattr(setup, campo, valor)
    setup.updated_at = _agora()
    setup.updated_by = settings.operator_name
    session.add(setup)
    session.commit()
    logger.info("Setup editado id=%s por %s", setup.id, settings.operator_name)

    return RedirectResponse(url=f"/setups/{setup.id}?sucesso=registro_atualizado", status_code=303)


# ---------------------------------------------------------------------------
# US5 — Arquivar/excluir reversível (GET + POST /setups/{id}/arquivar)
# ---------------------------------------------------------------------------

@router.get("/setups/{setup_id}/arquivar")
def confirmar_arquivar(
    request: Request,
    setup_id: int,
    session: Session = Depends(get_session),
) -> HTMLResponse:
    setup = _obter_setup(session, setup_id)
    return templates.TemplateResponse(
        request,
        "setups/arquivar.html",
        {
            "title": "Confirmar arquivamento",
            "setup": setup,
            "mensagem": None,
        },
    )


@router.post("/setups/{setup_id}/arquivar")
def arquivar_setup(
    request: Request,
    setup_id: int,
    session: Session = Depends(get_session),
    confirmacao: Annotated[str, Form()] = "",
) -> HTMLResponse:
    setup = _obter_setup(session, setup_id)

    # FR-010: exige confirmação explícita (exclusão reversível/arquivamento).
    if confirmacao != "sim":
        return templates.TemplateResponse(
            request,
            "setups/arquivar.html",
            {
                "title": "Confirmar arquivamento",
                "setup": setup,
                "mensagem": {"tipo": "error", "texto": "Nenhuma alteração foi feita. Marque a confirmação para arquivar."},
            },
        )

    # Guarda de aviso para utilização ativa: no v1 não há execuções/relações
    # vinculadas (provisionamento fora do escopo); quando existirem, avaliar aqui.
    setup.status = "arquivado"
    setup.updated_at = _agora()
    setup.updated_by = settings.operator_name
    session.add(setup)
    session.commit()
    logger.info("Setup arquivado id=%s por %s", setup.id, settings.operator_name)

    return RedirectResponse(url="/setups?sucesso=registro_arquivado", status_code=303)
