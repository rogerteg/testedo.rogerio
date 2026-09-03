"""App FastAPI do Automatic1 Admin (interface web server-rendered)."""
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .config import settings
from .database import init_db
from .routers import web

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("automatic1_admin")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    logger.info("Banco inicializado em %s", settings.db_path)
    yield


app = FastAPI(title="Automatic1 Admin", version=settings.app_version, lifespan=lifespan)

STATIC_DIR = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

app.include_router(web.router)
