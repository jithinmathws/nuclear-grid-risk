from pydantic import BaseModel


class GraphSummaryResponse(BaseModel):
    node_count: int
    edge_count: int
    isolated_nodes: list[str]
    dependency_type_counts: dict[str, int]
    in_degree: dict[str, int]
    out_degree: dict[str, int]

class GraphAnalysisResponse(BaseModel):
    in_degree: dict[str, int]
    out_degree: dict[str, int]
    degree_centrality: dict[str, float]
    betweenness_centrality: dict[str, float]
    edge_betweenness_centrality: dict[str, float]
    pagerank: dict[str, float]

class UpstreamAssetsResponse(BaseModel):
    asset_id: str
    upstream_assets: list[str]


class DownstreamAssetsResponse(BaseModel):
    asset_id: str
    downstream_assets: list[str]


class PathExistsResponse(BaseModel):
    source_asset_id: str
    target_asset_id: str
    path_exists: bool


class ShortestPathResponse(BaseModel):
    source_asset_id: str
    target_asset_id: str
    path: list[str]
    path_length: int