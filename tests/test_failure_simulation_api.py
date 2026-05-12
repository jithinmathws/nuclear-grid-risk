from app.models.asset import Asset
from app.models.dependency import Dependency


def test_failure_impact_api_returns_downstream_assets(client, db_session):
    asset_a = Asset(
        name="External Grid",
        asset_type="grid",
        criticality=0.9,
    )
    asset_b = Asset(
        name="Substation",
        asset_type="substation",
        criticality=0.8,
    )

    db_session.add_all([asset_a, asset_b])
    db_session.commit()

    dependency = Dependency(
        source_asset_id=asset_a.id,
        target_asset_id=asset_b.id,
        dependency_type="power",
        strength=1.0,
    )

    db_session.add(dependency)
    db_session.commit()

    response = client.post(
        "/api/v1/failure-simulation/impact",
        json={"failed_asset_id": str(asset_a.id)},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["failed_asset_id"] == str(asset_a.id)
    assert data["impacted_asset_count"] == 1
    assert data["impacted_assets"][0]["name"] == "Substation"