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

from ..catalogo_padrao import carregar_catalogo_padrao
from ..config import settings
from ..database import get_session
from ..models import PLATAFORMA_PADRAO, EnvironmentSetup, Execution, TargetHost
from ..schemas import (
    CATEGORIA_LABEL,
    CATEGORIA_VALIDOS,
    EXEC_STATUS_LABEL,
    HOST_STATUS_LABEL,
    STATUS_LABEL,
    normalizar_nome,
    rotulo_categoria,
    validar_campos,
    validar_execucao,
    validar_maquina,
)

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


def _execucoes(
    session: Session,
    *,
    setup_id: int | None = None,
    target_host_id: int | None = None,
) -> list[Execution]:
    """Execuções de um setup ou de uma máquina, da mais recente para a mais antiga."""
    stmt = select(Execution)
    if setup_id is not None:
        stmt = stmt.where(Execution.setup_id == setup_id)
    if target_host_id is not None:
        stmt = stmt.where(Execution.target_host_id == target_host_id)
    return session.exec(stmt.order_by(Execution.created_at.desc(), Execution.id.desc())).all()


def _hosts_por_id(session: Session) -> dict[int, TargetHost]:
    return {h.id: h for h in session.exec(select(TargetHost)).all()}


def _setups_por_id(session: Session) -> dict[int, EnvironmentSetup]:
    return {s.id: s for s in session.exec(select(EnvironmentSetup)).all()}


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
    categoria: Annotated[str, Query()] = "",
    sucesso: Annotated[str, Query()] = "",
    criados: Annotated[int, Query()] = 0,
    ignorados: Annotated[int, Query()] = 0,
    avisos: Annotated[int, Query()] = 0,
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

    # Filtro por categoria (FR-007 — feature 002)
    if categoria in CATEGORIA_VALIDOS:
        registros = [r for r in registros if r.categoria == categoria]

    registros.sort(key=lambda r: r.updated_at, reverse=True)

    mensagem = None
    if sucesso == "registro_criado":
        mensagem = {"tipo": "success", "texto": "Setup cadastrado com sucesso."}
    elif sucesso == "registro_arquivado":
        mensagem = {"tipo": "success", "texto": "Setup arquivado com sucesso."}
    elif sucesso == "catalogo_carregado":
        # FR-008/FR-014: relatório da carga do catálogo padrão (feature 002).
        texto = (
            f"Catálogo padrão carregado: {criados} criado(s), "
            f"{ignorados} ignorado(s)."
        )
        if avisos:
            texto += f" {avisos} aviso(s) — itens bloqueados por suspeita de segredo não foram criados."
        mensagem = {"tipo": "success", "texto": texto}

    return templates.TemplateResponse(
        request,
        "setups/list.html",
        {
            "title": "Setups de ambiente",
            "setups": registros,
            "termo": termo,
            "categoria_filtro": categoria,
            "categoria_label": CATEGORIA_LABEL,
            "status_label": STATUS_LABEL,
            "mensagem": mensagem,
        },
    )


# ---------------------------------------------------------------------------
# Feature 002 — Carregar catálogo padrão (POST /setups/carregar-padrao)
# ---------------------------------------------------------------------------

@router.post("/setups/carregar-padrao")
def carregar_padrao(
    session: Session = Depends(get_session),
) -> HTMLResponse:
    relatorio = carregar_catalogo_padrao(session, autor=settings.operator_name)
    query = (
        f"sucesso=catalogo_carregado&criados={relatorio['criados']}"
        f"&ignorados={relatorio['ignorados']}"
    )
    if relatorio["avisos"]:
        query += f"&avisos={len(relatorio['avisos'])}"
    return RedirectResponse(url=f"/setups?{query}", status_code=303)


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
    elif sucesso == "execucao_registrada":
        mensagem = {"tipo": "success", "texto": "Execução registrada com sucesso."}

    # Feature 003 — histórico de execuções do setup + última execução derivada (Q3=A).
    execucoes = _execucoes(session, setup_id=setup_id)
    ultima_execucao = execucoes[0] if execucoes else None
    hosts = _hosts_por_id(session) if execucoes else {}

    return templates.TemplateResponse(
        request,
        "setups/detail.html",
        {
            "title": setup.nome,
            "setup": setup,
            "status_label": STATUS_LABEL,
            "categoria_rotulo": rotulo_categoria(setup.categoria),
            "execucoes": execucoes,
            "ultima_execucao": ultima_execucao,
            "exec_status_label": EXEC_STATUS_LABEL,
            "hosts": hosts,
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
    # Feature 003 — aviso de "utilização ativa" (US3): conta execuções registradas.
    execucoes_count = len(_execucoes(session, setup_id=setup_id))
    return templates.TemplateResponse(
        request,
        "setups/arquivar.html",
        {
            "title": "Confirmar arquivamento",
            "setup": setup,
            "execucoes_count": execucoes_count,
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


# ---------------------------------------------------------------------------
# Feature 003 — Máquinas alvo (US1/US3)
# ---------------------------------------------------------------------------

MAQUINA_CAMPOS = ["nome", "identificacao", "plataforma_alvo", "descricao"]


def _obter_maquina(session: Session, maquina_id: int) -> TargetHost:
    maquina = session.get(TargetHost, maquina_id)
    if maquina is None:
        raise HTTPException(status_code=404, detail="Máquina não encontrada.")
    return maquina


def _existe_maquina_nome_duplicado(session: Session, nome: str, excluir_id: int | None = None) -> bool:
    alvo = normalizar_nome(nome)
    for maquina in session.exec(select(TargetHost)).all():
        if excluir_id is not None and maquina.id == excluir_id:
            continue
        if normalizar_nome(maquina.nome) == alvo:
            return True
    return False


@router.get("/maquinas")
def listar_maquinas(
    request: Request,
    session: Session = Depends(get_session),
    q: Annotated[str, Query()] = "",
) -> HTMLResponse:
    termo = q.strip()
    maquinas = session.exec(select(TargetHost)).all()
    if termo:
        filtro = termo.lower()
        maquinas = [
            m for m in maquinas
            if filtro in m.nome.lower() or filtro in m.identificacao.lower()
        ]
    maquinas.sort(key=lambda m: m.updated_at, reverse=True)

    return templates.TemplateResponse(
        request,
        "maquinas/list.html",
        {
            "title": "Máquinas alvo",
            "maquinas": maquinas,
            "termo": termo,
            "host_status_label": HOST_STATUS_LABEL,
            "mensagem": None,
        },
    )


@router.get("/maquinas/novo")
def nova_maquina(request: Request) -> HTMLResponse:
    dados = {"nome": "", "identificacao": "", "plataforma_alvo": PLATAFORMA_PADRAO, "descricao": ""}
    return templates.TemplateResponse(
        request,
        "maquinas/form.html",
        {
            "title": "Nova máquina alvo",
            "acao": "/maquinas",
            "dados": dados,
            "erros": {},
            "mensagem": None,
        },
    )


@router.post("/maquinas")
def criar_maquina(
    request: Request,
    session: Session = Depends(get_session),
    nome: Annotated[str, Form()] = "",
    identificacao: Annotated[str, Form()] = "",
    plataforma_alvo: Annotated[str, Form()] = "",
    descricao: Annotated[str, Form()] = "",
) -> HTMLResponse:
    dados = {
        "nome": nome.strip(),
        "identificacao": identificacao.strip(),
        "plataforma_alvo": plataforma_alvo.strip() or PLATAFORMA_PADRAO,
        "descricao": descricao.strip(),
    }

    erros = validar_maquina(dados)
    if not erros and _existe_maquina_nome_duplicado(session, dados["nome"]):
        erros["nome"] = "Já existe uma máquina com esse nome."

    if erros:
        return templates.TemplateResponse(
            request,
            "maquinas/form.html",
            {
                "title": "Nova máquina alvo",
                "acao": "/maquinas",
                "dados": dados,
                "erros": erros,
                "mensagem": {"tipo": "error", "texto": "Corrija os campos destacados e tente novamente."},
            },
        )

    maquina = TargetHost(
        **dados,
        status="ativa",
        created_by=settings.operator_name,
        updated_by=settings.operator_name,
    )
    session.add(maquina)
    session.commit()
    session.refresh(maquina)
    logger.info("Máquina criada id=%s nome=%r por %s", maquina.id, maquina.nome, settings.operator_name)
    return RedirectResponse(url=f"/maquinas/{maquina.id}?sucesso=maquina_criada", status_code=303)


@router.get("/maquinas/{maquina_id}")
def detalhe_maquina(
    request: Request,
    maquina_id: int,
    session: Session = Depends(get_session),
    sucesso: str = Query(""),
) -> HTMLResponse:
    maquina = _obter_maquina(session, maquina_id)

    mensagem = None
    if sucesso == "maquina_criada":
        mensagem = {"tipo": "success", "texto": "Máquina criada com sucesso."}
    elif sucesso == "maquina_atualizada":
        mensagem = {"tipo": "success", "texto": "Máquina atualizada com sucesso."}
    elif sucesso == "maquina_desativada":
        mensagem = {"tipo": "success", "texto": "Máquina desativada com sucesso."}
    elif sucesso == "maquina_reativada":
        mensagem = {"tipo": "success", "texto": "Máquina reativada com sucesso."}

    execucoes = _execucoes(session, target_host_id=maquina_id)
    setups = _setups_por_id(session) if execucoes else {}

    return templates.TemplateResponse(
        request,
        "maquinas/detail.html",
        {
            "title": maquina.nome,
            "maquina": maquina,
            "host_status_label": HOST_STATUS_LABEL,
            "execucoes": execucoes,
            "exec_status_label": EXEC_STATUS_LABEL,
            "setups": setups,
            "mensagem": mensagem,
        },
    )


@router.get("/maquinas/{maquina_id}/editar")
def editar_maquina_form(
    request: Request,
    maquina_id: int,
    session: Session = Depends(get_session),
) -> HTMLResponse:
    maquina = _obter_maquina(session, maquina_id)
    dados = {campo: (getattr(maquina, campo) or "") for campo in MAQUINA_CAMPOS}
    return templates.TemplateResponse(
        request,
        "maquinas/form.html",
        {
            "title": f"Editar: {maquina.nome}",
            "acao": f"/maquinas/{maquina_id}/editar",
            "dados": dados,
            "erros": {},
            "botao": "Salvar alterações",
            "mensagem": None,
        },
    )


@router.post("/maquinas/{maquina_id}/editar")
def editar_maquina(
    request: Request,
    maquina_id: int,
    session: Session = Depends(get_session),
    nome: Annotated[str, Form()] = "",
    identificacao: Annotated[str, Form()] = "",
    plataforma_alvo: Annotated[str, Form()] = "",
    descricao: Annotated[str, Form()] = "",
) -> HTMLResponse:
    maquina = _obter_maquina(session, maquina_id)
    dados = {
        "nome": nome.strip(),
        "identificacao": identificacao.strip(),
        "plataforma_alvo": plataforma_alvo.strip() or PLATAFORMA_PADRAO,
        "descricao": descricao.strip(),
    }

    erros = validar_maquina(dados)
    if not erros and _existe_maquina_nome_duplicado(session, dados["nome"], excluir_id=maquina.id):
        erros["nome"] = "Já existe uma máquina com esse nome."

    if erros:
        return templates.TemplateResponse(
            request,
            "maquinas/form.html",
            {
                "title": f"Editar: {maquina.nome}",
                "acao": f"/maquinas/{maquina_id}/editar",
                "dados": dados,
                "erros": erros,
                "botao": "Salvar alterações",
                "mensagem": {"tipo": "error", "texto": "Corrija os campos destacados e tente novamente."},
            },
        )

    for campo, valor in dados.items():
        setattr(maquina, campo, valor)
    maquina.updated_at = _agora()
    maquina.updated_by = settings.operator_name
    session.add(maquina)
    session.commit()
    logger.info("Máquina editada id=%s por %s", maquina.id, settings.operator_name)
    return RedirectResponse(url=f"/maquinas/{maquina.id}?sucesso=maquina_atualizada", status_code=303)


@router.get("/maquinas/{maquina_id}/desativar")
def confirmar_desativar_maquina(
    request: Request,
    maquina_id: int,
    session: Session = Depends(get_session),
) -> HTMLResponse:
    maquina = _obter_maquina(session, maquina_id)
    execucoes_count = len(_execucoes(session, target_host_id=maquina_id))
    return templates.TemplateResponse(
        request,
        "maquinas/desativar.html",
        {
            "title": "Confirmar desativação",
            "maquina": maquina,
            "execucoes_count": execucoes_count,
            "mensagem": None,
        },
    )


@router.post("/maquinas/{maquina_id}/desativar")
def desativar_maquina(
    request: Request,
    maquina_id: int,
    session: Session = Depends(get_session),
    confirmacao: Annotated[str, Form()] = "",
) -> HTMLResponse:
    maquina = _obter_maquina(session, maquina_id)

    if confirmacao != "sim":
        execucoes_count = len(_execucoes(session, target_host_id=maquina_id))
        return templates.TemplateResponse(
            request,
            "maquinas/desativar.html",
            {
                "title": "Confirmar desativação",
                "maquina": maquina,
                "execucoes_count": execucoes_count,
                "mensagem": {"tipo": "error", "texto": "Nenhuma alteração foi feita. Confirme para desativar."},
            },
        )

    maquina.status = "inativa"
    maquina.updated_at = _agora()
    maquina.updated_by = settings.operator_name
    session.add(maquina)
    session.commit()
    logger.info("Máquina desativada id=%s por %s", maquina.id, settings.operator_name)
    return RedirectResponse(url=f"/maquinas/{maquina.id}?sucesso=maquina_desativada", status_code=303)


@router.post("/maquinas/{maquina_id}/reativar")
def reativar_maquina(
    maquina_id: int,
    session: Session = Depends(get_session),
) -> HTMLResponse:
    maquina = _obter_maquina(session, maquina_id)
    maquina.status = "ativa"
    maquina.updated_at = _agora()
    maquina.updated_by = settings.operator_name
    session.add(maquina)
    session.commit()
    logger.info("Máquina reativada id=%s por %s", maquina.id, settings.operator_name)
    return RedirectResponse(url=f"/maquinas/{maquina.id}?sucesso=maquina_reativada", status_code=303)


# ---------------------------------------------------------------------------
# Feature 003 — Execuções (US2)
# ---------------------------------------------------------------------------

EXEC_STATUS_OPCOES = list(EXEC_STATUS_LABEL.items())


@router.get("/setups/{setup_id}/executar")
def nova_execucao_form(
    request: Request,
    setup_id: int,
    session: Session = Depends(get_session),
) -> HTMLResponse:
    setup = _obter_setup(session, setup_id)
    maquinas = session.exec(
        select(TargetHost).where(TargetHost.status == "ativa").order_by(TargetHost.nome)
    ).all()
    return templates.TemplateResponse(
        request,
        "setups/executar.html",
        {
            "title": f"Registrar execução: {setup.nome}",
            "setup": setup,
            "maquinas": maquinas,
            "exec_status_opcoes": EXEC_STATUS_OPCOES,
            "dados": {"target_host_id": "", "status": "sucesso", "resumo": ""},
            "erros": {},
            "mensagem": None,
        },
    )


@router.post("/setups/{setup_id}/executar")
def registrar_execucao(
    request: Request,
    setup_id: int,
    session: Session = Depends(get_session),
    target_host_id: Annotated[str, Form()] = "",
    status: Annotated[str, Form()] = "",
    resumo: Annotated[str, Form()] = "",
) -> HTMLResponse:
    setup = _obter_setup(session, setup_id)

    dados = {"status": status.strip(), "resumo": resumo.strip()}
    erros = validar_execucao(dados)

    host: TargetHost | None = None
    if not erros:
        try:
            host = _obter_maquina(session, int(target_host_id)) if target_host_id.strip() else None
        except (ValueError, HTTPException):
            host = None
        if host is None:
            erros["target_host_id"] = "Selecione uma máquina válida."
        elif host.status != "ativa":
            erros["target_host_id"] = "A máquina selecionada está inativa. Reative-a ou escolha outra."

    if erros:
        maquinas = session.exec(
            select(TargetHost).where(TargetHost.status == "ativa").order_by(TargetHost.nome)
        ).all()
        return templates.TemplateResponse(
            request,
            "setups/executar.html",
            {
                "title": f"Registrar execução: {setup.nome}",
                "setup": setup,
                "maquinas": maquinas,
                "exec_status_opcoes": EXEC_STATUS_OPCOES,
                "dados": {"target_host_id": target_host_id, "status": dados["status"], "resumo": resumo.strip()},
                "erros": erros,
                "mensagem": {"tipo": "error", "texto": "Corrija os campos destacados e tente novamente."},
            },
        )

    execucao = Execution(
        setup_id=setup.id,
        target_host_id=host.id,
        status=dados["status"],
        resumo=dados["resumo"] or None,
        created_by=settings.operator_name,
    )
    session.add(execucao)
    session.commit()
    logger.info(
        "Execução registrada setup=%s maquina=%s status=%s por %s",
        setup.id,
        host.id,
        execucao.status,
        settings.operator_name,
    )
    return RedirectResponse(url=f"/setups/{setup.id}?sucesso=execucao_registrada", status_code=303)
