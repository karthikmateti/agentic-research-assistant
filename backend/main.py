from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.api.routes import router
from backend.database.db import init_db
from backend.utils.logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    logger.info("Application startup complete")
    yield


app = FastAPI(
    title="Agentic AI Research Assistant",
    description="Multi-agent research automation platform",
    version="1.0.0",
    lifespan=lifespan,
)


app.include_router(router)
