import networkx as nx

from app.graph.metrics import GraphMetricsService


def test_graph_summary_metrics():
    graph = nx.DiGraph()

    graph.add_node("plant-1")
    graph.add_node("substation-1")
    graph.add_node("backup-generator-1")

    graph.add_edge(
        "plant-1",
        "substation-1",
        dependency_type="POWER_FLOW",
    )

    metrics_service = GraphMetricsService()

    summary = metrics_service.get_summary(graph)

    assert summary["node_count"] == 3
    assert summary["edge_count"] == 1
    assert summary["isolated_nodes"] == ["backup-generator-1"]
    assert summary["dependency_type_counts"] == {"POWER_FLOW": 1}

    assert summary["in_degree"]["plant-1"] == 0
    assert summary["out_degree"]["plant-1"] == 1

    assert summary["in_degree"]["substation-1"] == 1
    assert summary["out_degree"]["substation-1"] == 0

    assert summary["in_degree"]["backup-generator-1"] == 0
    assert summary["out_degree"]["backup-generator-1"] == 0