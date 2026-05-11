import pytest
import networkx as nx

from app.graph.network_analysis import NetworkAnalysisService


def test_in_degree():
    graph = nx.DiGraph()
    graph.add_edge("plant-1", "substation-1")
    graph.add_edge("generator-1", "substation-1")

    service = NetworkAnalysisService()

    result = service.in_degree(graph)

    assert result["plant-1"] == 0
    assert result["generator-1"] == 0
    assert result["substation-1"] == 2


def test_out_degree():
    graph = nx.DiGraph()
    graph.add_edge("plant-1", "substation-1")
    graph.add_edge("plant-1", "cooling-system-1")

    service = NetworkAnalysisService()

    result = service.out_degree(graph)

    assert result["plant-1"] == 2
    assert result["substation-1"] == 0
    assert result["cooling-system-1"] == 0


def test_degree_centrality_identifies_hub_node():
    graph = nx.DiGraph()
    graph.add_edge("plant-1", "substation-1")
    graph.add_edge("plant-1", "cooling-system-1")
    graph.add_edge("plant-1", "control-center-1")

    service = NetworkAnalysisService()

    result = service.degree_centrality(graph)

    assert result["plant-1"] > result["substation-1"]


def test_betweenness_centrality_identifies_bridge_node():
    graph = nx.DiGraph()
    graph.add_edge("plant-1", "substation-1")
    graph.add_edge("substation-1", "control-center-1")

    service = NetworkAnalysisService()

    result = service.betweenness_centrality(graph)

    assert result["substation-1"] > result["plant-1"]
    assert result["substation-1"] > result["control-center-1"]


def test_edge_betweenness_centrality_returns_edge_scores():
    graph = nx.DiGraph()
    graph.add_edge("plant-1", "substation-1")
    graph.add_edge("substation-1", "control-center-1")

    service = NetworkAnalysisService()

    result = service.edge_betweenness_centrality(graph)

    assert "plant-1->substation-1" in result
    assert "substation-1->control-center-1" in result


def test_pagerank_returns_scores_for_all_nodes():
    graph = nx.DiGraph()
    graph.add_edge("plant-1", "substation-1")
    graph.add_edge("substation-1", "control-center-1")

    service = NetworkAnalysisService()

    result = service.pagerank(graph)

    assert set(result.keys()) == {
        "plant-1",
        "substation-1",
        "control-center-1",
    }

    assert pytest.approx(sum(result.values()), 0.01) == 1.0


def test_pagerank_returns_empty_dict_for_empty_graph():
    graph = nx.DiGraph()

    service = NetworkAnalysisService()

    result = service.pagerank(graph)

    assert result == {}