from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.graph.builder import InfrastructureGraphBuilder
from app.graph.metrics import GraphMetricsService
from app.graph.traversal import GraphTraversalService
from app.graph.schemas import (
    DownstreamAssetsResponse,
    GraphSummaryResponse,
    PathExistsResponse,
    ShortestPathResponse,
    UpstreamAssetsResponse,
)
from app.graph.network_analysis import NetworkAnalysisService
from app.graph.schemas import GraphAnalysisResponse

router = APIRouter(prefix="/graph", tags=["Graph"])


@router.get("/summary", response_model=GraphSummaryResponse)
def get_graph_summary(db: Session = Depends(get_db)) -> dict[str, Any]:
    graph = InfrastructureGraphBuilder(db).build()
    return GraphMetricsService().get_summary(graph)

@router.get(
    "/analysis",
    response_model=GraphAnalysisResponse,
)
def get_graph_analysis(
    db: Session = Depends(get_db),
) -> GraphAnalysisResponse:
    graph = InfrastructureGraphBuilder(db).build()

    analysis_service = NetworkAnalysisService()

    return GraphAnalysisResponse(
        in_degree=analysis_service.in_degree(graph),
        out_degree=analysis_service.out_degree(graph),
        degree_centrality=analysis_service.degree_centrality(graph),
        betweenness_centrality=analysis_service.betweenness_centrality(graph),
        edge_betweenness_centrality=analysis_service.edge_betweenness_centrality(graph),
        pagerank=analysis_service.pagerank(graph),
    )

@router.get("/{asset_id}/upstream", response_model=UpstreamAssetsResponse)
def get_upstream_assets(
    asset_id: str,
    db: Session = Depends(get_db),
) -> dict[str, object]:
    graph = InfrastructureGraphBuilder(db).build()
    upstream_assets = GraphTraversalService().get_upstream_assets(graph, asset_id)

    return {
        "asset_id": asset_id,
        "upstream_assets": upstream_assets,
    }


@router.get("/{asset_id}/downstream", response_model=DownstreamAssetsResponse)
def get_downstream_assets(
    asset_id: str,
    db: Session = Depends(get_db),
) -> dict[str, object]:
    graph = InfrastructureGraphBuilder(db).build()
    downstream_assets = GraphTraversalService().get_downstream_assets(graph, asset_id)

    return {
        "asset_id": asset_id,
        "downstream_assets": downstream_assets,
    }


@router.get("/path/check", response_model=PathExistsResponse)
def check_path_exists(
    source_asset_id: str,
    target_asset_id: str,
    db: Session = Depends(get_db),
) -> dict[str, object]:
    graph = InfrastructureGraphBuilder(db).build()
    path_exists = GraphTraversalService().has_path(
        graph,
        source_asset_id,
        target_asset_id,
    )

    return {
        "source_asset_id": source_asset_id,
        "target_asset_id": target_asset_id,
        "path_exists": path_exists,
    }


@router.get("/path/shortest", response_model=ShortestPathResponse)
def get_shortest_path(
    source_asset_id: str,
    target_asset_id: str,
    db: Session = Depends(get_db),
) -> dict[str, object]:
    graph = InfrastructureGraphBuilder(db).build()
    path = GraphTraversalService().shortest_path(
        graph,
        source_asset_id,
        target_asset_id,
    )

    return {
        "source_asset_id": source_asset_id,
        "target_asset_id": target_asset_id,
        "path": path,
        "path_length": len(path),
    }