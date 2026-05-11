from __future__ import annotations

import networkx as nx


class GraphTraversalService:
    """Provides traversal utilities for infrastructure dependency graphs."""

    def get_downstream_assets(
        self,
        graph: nx.DiGraph,
        source_asset_id: str,
    ) -> list[str]:
        if source_asset_id not in graph:
            return []

        return list(nx.descendants(graph, source_asset_id))

    def get_upstream_assets(
        self,
        graph: nx.DiGraph,
        target_asset_id: str,
    ) -> list[str]:
        if target_asset_id not in graph:
            return []

        return list(nx.ancestors(graph, target_asset_id))

    def has_path(
        self,
        graph: nx.DiGraph,
        source_asset_id: str,
        target_asset_id: str,
    ) -> bool:
        if source_asset_id not in graph or target_asset_id not in graph:
            return False

        return nx.has_path(graph, source_asset_id, target_asset_id)

    def shortest_path(
        self,
        graph: nx.DiGraph,
        source_asset_id: str,
        target_asset_id: str,
    ) -> list[str]:
        if source_asset_id not in graph or target_asset_id not in graph:
            return []

        try:
            return nx.shortest_path(graph, source_asset_id, target_asset_id)
        except nx.NetworkXNoPath:
            return []