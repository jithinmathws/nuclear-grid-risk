import networkx as nx

from app.graph.builder import InfrastructureGraphBuilder
from app.models.asset import Asset
from app.models.dependency import Dependency


def test_build_graph_from_assets_and_dependencies(db_session):
    asset_1 = Asset(
        name="Nuclear Plant A",
        asset_type="PLANT",
        criticality=5,
        status="ACTIVE",
    )

    asset_2 = Asset(
        name="Substation A",
        asset_type="SUBSTATION",
        criticality=3,
        status="ACTIVE",
    )

    db_session.add_all([asset_1, asset_2])
    db_session.commit()
    db_session.refresh(asset_1)
    db_session.refresh(asset_2)

    dependency = Dependency(
        source_asset_id=asset_1.id,
        target_asset_id=asset_2.id,
        dependency_type="POWER_FLOW",
        strength=5,
    )

    db_session.add(dependency)
    db_session.commit()
    db_session.refresh(dependency)

    builder = InfrastructureGraphBuilder(db_session)
    graph = builder.build()

    assert isinstance(graph, nx.DiGraph)
    assert graph.number_of_nodes() == 2
    assert graph.number_of_edges() == 1

    assert str(asset_1.id) in graph.nodes
    assert str(asset_2.id) in graph.nodes

    assert graph.nodes[str(asset_1.id)]["name"] == "Nuclear Plant A"
    assert graph.nodes[str(asset_1.id)]["asset_type"] == "PLANT"
    assert graph.nodes[str(asset_1.id)]["criticality"] == 5
    assert graph.nodes[str(asset_1.id)]["status"] == "ACTIVE"

    edge_data = graph.get_edge_data(str(asset_1.id), str(asset_2.id))

    assert edge_data is not None
    assert edge_data["id"] == str(dependency.id)
    assert edge_data["dependency_type"] == "POWER_FLOW"
    assert edge_data["strength"] == 5