from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.graph.builder import InfrastructureGraphBuilder
from app.graph.metrics import GraphMetricsService

router = APIRouter(prefix="/graph", tags=["Graph"])


@router.get("/summary")
def get_graph_summary(db: Session = Depends(get_db)) -> dict[str, Any]:
    graph = InfrastructureGraphBuilder(db).build()
    return GraphMetricsService().get_summary(graph)