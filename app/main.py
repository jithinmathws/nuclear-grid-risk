from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI
from loguru import logger
from sqlalchemy import text

from app.api.v1.routes.assets import router as assets_router
from app.api.v1.routes.dependencies import router as dependencies_router
from app.api.v1.routes.graph import router as graph_router
from app.core.config import settings
from app.core.database import SessionLocal
from app.core.logging import configure_logging
from app.api.v1.routes.failure_simulation import (
    router as failure_simulation_router,
)

configure_logging()

api_router = APIRouter()

api_router.include_router(assets_router)
api_router.include_router(dependencies_router)
api_router.include_router(graph_router)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("NuclearGridRisk API started")

    yield

    logger.info("NuclearGridRisk API shutting down")


app = FastAPI(
    title="NuclearGridRisk",
    description="PSA-inspired risk simulation backend for synthetic civilian nuclear infrastructure.",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(api_router, prefix="/api/v1")
app.include_router(failure_simulation_router, prefix="/api/v1")

@app.get("/api/health")
def health_check() -> dict[str, str]:
    logger.info("Health check requested")

    return {
        "status": "ok",
        "service": "NuclearGridRisk API",
    }


@app.get("/api/config-test")
def config_test():
    return {
        "app_name": settings.app_name,
    }


@app.get("/api/db-health")
def database_health_check() -> dict[str, str]:
    db = SessionLocal()

    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "ok",
            "database": "connected",
        }
    finally:
        db.close()
