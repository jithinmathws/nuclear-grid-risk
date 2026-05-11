import networkx as nx

from app.graph.traversal import GraphTraversalService


def test_get_downstream_assets():
    graph = nx.DiGraph()
    graph.add_edge("plant-1", "substation-1")
    graph.add_edge("substation-1", "control-center-1")

    service = GraphTraversalService()

    result = service.get_downstream_assets(graph, "plant-1")

    assert set(result) == {"substation-1", "control-center-1"}


def test_get_upstream_assets():
    graph = nx.DiGraph()
    graph.add_edge("plant-1", "substation-1")
    graph.add_edge("substation-1", "control-center-1")

    service = GraphTraversalService()

    result = service.get_upstream_assets(graph, "control-center-1")

    assert set(result) == {"plant-1", "substation-1"}


def test_has_path_returns_true_when_path_exists():
    graph = nx.DiGraph()
    graph.add_edge("plant-1", "substation-1")
    graph.add_edge("substation-1", "control-center-1")

    service = GraphTraversalService()

    assert service.has_path(graph, "plant-1", "control-center-1") is True


def test_has_path_returns_false_when_path_does_not_exist():
    graph = nx.DiGraph()
    graph.add_edge("plant-1", "substation-1")
    graph.add_node("backup-generator-1")

    service = GraphTraversalService()

    assert service.has_path(graph, "backup-generator-1", "plant-1") is False


def test_shortest_path_returns_expected_path():
    graph = nx.DiGraph()
    graph.add_edge("plant-1", "substation-1")
    graph.add_edge("substation-1", "control-center-1")

    service = GraphTraversalService()

    result = service.shortest_path(graph, "plant-1", "control-center-1")

    assert result == ["plant-1", "substation-1", "control-center-1"]


def test_shortest_path_returns_empty_list_when_no_path_exists():
    graph = nx.DiGraph()
    graph.add_edge("plant-1", "substation-1")
    graph.add_node("backup-generator-1")

    service = GraphTraversalService()

    result = service.shortest_path(graph, "backup-generator-1", "plant-1")

    assert result == []


def test_traversal_returns_empty_list_for_missing_node():
    graph = nx.DiGraph()
    graph.add_edge("plant-1", "substation-1")

    service = GraphTraversalService()

    assert service.get_downstream_assets(graph, "missing-node") == []
    assert service.get_upstream_assets(graph, "missing-node") == []