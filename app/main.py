"""App FastAPI do Automatic1 Admin (interface web server-rendered)."""
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path
from urllib.parse import quote

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from .auth import COOKIE_SESSAO, esta_configurado, sessao_valida
from .config import settings
from .database import init_db
from .routers import api, web

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("automatic1_admin")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    logger.info("Banco inicializado em %s", settings.db_path)
    # Feature 008 — recupera execuções órfãs (em_andamento sem worker) no startup.
    from .worker import recuperar_orfas

    recuperar_orfas()
    # Feature 012 — rotina de agendamentos (cron) em segundo plano (desligável).
    if os.getenv("AUTOMATIC1_SCHEDULER", "1") != "0":
        from .agendador import iniciar_rotina

        iniciar_rotina()
    yield


app = FastAPI(title="Automatic1 Admin", version=settings.app_version, lifespan=lifespan)

STATIC_DIR = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

app.include_router(web.router)
app.include_router(api.router)


# ---------------------------------------------------------------------------
# Feature 006 — Middleware de sessão (protege rotas web; públicos: login/static/api)
# ---------------------------------------------------------------------------

def _e_publico(path: str) -> bool:
    if path in ("/login", "/logout", "/healthz", "/"):
        return True
    return path.startswith(("/static", "/api"))


@app.middleware("http")
async def exigir_sessao(request: Request, call_next):
    if _e_publico(request.url.path):
        return await call_next(request)

    if not esta_configurado() or not sessao_valida(request.cookies.get(COOKIE_SESSAO)):
        destino = request.url.path
        if request.url.query:
            destino = f"{destino}?{request.url.query}"
        return RedirectResponse(url=f"/login?next={quote(destino)}", status_code=302)

    return await call_next(request)
