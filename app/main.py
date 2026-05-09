from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger

from app.core.logging import configure_logging
from app.core.config import settings

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