from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger
from sqlalchemy import text

from app.core.config import settings
from app.core.database import SessionLocal
from app.core.logging import configure_logging

configure_logging()


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
