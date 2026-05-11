from app.models.asset import Asset
from app.models.dependency import Dependency


def test_get_graph_analysis_api(client, db_session):
    plant = Asset(
        name="Nuclear Plant A",
        asset_type="PLANT",
        criticality=0.95,
        status="ACTIVE",
    )
    substation = Asset(
        name="Substation A",
        asset_type="SUBSTATION",
        criticality=0.75,
        status="ACTIVE",
    )
    control_center = Asset(
        name="Control Center A",
        asset_type="CONTROL_CENTER",
        criticality=0.85,
        status="ACTIVE",
    )

    db_session.add_all([plant, substation, control_center])
    db_session.commit()

    db_session.refresh(plant)
    db_session.refresh(substation)
    db_session.refresh(control_center)

    db_session.add_all(
        [
            Dependency(
                source_asset_id=plant.id,
                target_asset_id=substation.id,
                dependency_type="POWER_FLOW",
                strength=0.90,
            ),
            Dependency(
                source_asset_id=substation.id,
                target_asset_id=control_center.id,
                dependency_type="COMMUNICATION",
                strength=0.80,
            ),
        ]
    )

    db_session.commit()

    response = client.get("/api/v1/graph/analysis")

    assert response.status_code == 200

    data = response.json()

    assert "in_degree" in data
    assert "out_degree" in data
    assert "degree_centrality" in data
    assert "betweenness_centrality" in data
    assert "edge_betweenness_centrality" in data
    assert "pagerank" in data

    assert data["in_degree"][str(substation.id)] == 1
    assert data["out_degree"][str(plant.id)] == 1