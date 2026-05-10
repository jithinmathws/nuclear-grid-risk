from app.models.asset import Asset
from app.models.dependency import Dependency


def test_get_graph_summary(client, db_session):
    asset_1 = Asset(
        name="Nuclear Plant A",
        asset_type="PLANT",
        criticality=0.95,
        status="ACTIVE",
    )
    asset_2 = Asset(
        name="Substation A",
        asset_type="SUBSTATION",
        criticality=0.75,
        status="ACTIVE",
    )
    asset_3 = Asset(
        name="Backup Generator A",
        asset_type="GENERATOR",
        criticality=0.60,
        status="ACTIVE",
    )

    db_session.add_all([asset_1, asset_2, asset_3])
    db_session.commit()

    db_session.refresh(asset_1)
    db_session.refresh(asset_2)
    db_session.refresh(asset_3)

    dependency = Dependency(
        source_asset_id=asset_1.id,
        target_asset_id=asset_2.id,
        dependency_type="POWER_FLOW",
        strength=0.85,
    )

    db_session.add(dependency)
    db_session.commit()

    response = client.get("/api/v1/graph/summary")

    assert response.status_code == 200

    data = response.json()

    assert data["node_count"] == 3
    assert data["edge_count"] == 1

    assert str(asset_3.id) in data["isolated_nodes"]

    assert data["dependency_type_counts"] == {
        "POWER_FLOW": 1,
    }

    assert data["in_degree"][str(asset_1.id)] == 0
    assert data["out_degree"][str(asset_1.id)] == 1

    assert data["in_degree"][str(asset_2.id)] == 1
    assert data["out_degree"][str(asset_2.id)] == 0

    assert data["in_degree"][str(asset_3.id)] == 0
    assert data["out_degree"][str(asset_3.id)] == 0