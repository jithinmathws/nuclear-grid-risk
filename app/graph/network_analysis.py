from __future__ import annotations

import networkx as nx


class NetworkAnalysisService:
    """Provides structural network analysis for infrastructure dependency graphs."""

    def in_degree(self, graph: nx.DiGraph) -> dict[str, int]:
        return dict(graph.in_degree())

    def out_degree(self, graph: nx.DiGraph) -> dict[str, int]:
        return dict(graph.out_degree())

    def degree_centrality(self, graph: nx.DiGraph) -> dict[str, float]:
        return nx.degree_centrality(graph)

    def betweenness_centrality(self, graph: nx.DiGraph) -> dict[str, float]:
        return nx.betweenness_centrality(graph, normalized=True)

    def edge_betweenness_centrality(self, graph: nx.DiGraph) -> dict[str, float]:
        scores = nx.edge_betweenness_centrality(graph, normalized=True)

        return {
            f"{source}->{target}": score
            for (source, target), score in scores.items()
        }

    def pagerank(self, graph: nx.DiGraph) -> dict[str, float]:
        if graph.number_of_nodes() == 0:
            return {}

        return nx.pagerank(graph)