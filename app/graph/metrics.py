from __future__ import annotations

from collections import Counter
from typing import Any

import networkx as nx


class GraphMetricsService:
    """Provides summary metrics for an infrastructure graph."""

    def get_summary(self, graph: nx.DiGraph) -> dict[str, Any]:
        dependency_type_counts = Counter(
            edge_data.get("dependency_type", "UNKNOWN")
            for _, _, edge_data in graph.edges(data=True)
        )

        isolated_nodes = list(nx.isolates(graph))

        in_degree = {
            node_id: degree
            for node_id, degree in graph.in_degree()
        }

        out_degree = {
            node_id: degree
            for node_id, degree in graph.out_degree()
        }

        return {
            "node_count": graph.number_of_nodes(),
            "edge_count": graph.number_of_edges(),
            "isolated_nodes": isolated_nodes,
            "dependency_type_counts": dict(dependency_type_counts),
            "in_degree": in_degree,
            "out_degree": out_degree,
        }