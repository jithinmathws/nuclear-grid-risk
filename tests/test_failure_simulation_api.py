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

    impacted_assets_by_id = {
        asset["asset_id"]: asset
        for asset in data["impacted_assets"]
    }

    assert str(asset_b.id) in impacted_assets_by_id

    impacted_asset = impacted_assets_by_id[str(asset_b.id)]

    print(data["impacted_assets"])
    assert impacted_asset["name"] == "Substation"
    assert impacted_asset["asset_type"] == "substation"
    assert impacted_asset["criticality"] == 0.8
    assert impacted_asset["caused_by_asset_id"] == str(asset_a.id)
    assert impacted_asset["dependency_type"] == "power"
    assert impacted_asset["propagation_strength"] == 1.0


def test_failure_impact_api_respects_propagation_threshold(client, db_session):
    asset_a = Asset(
        name="External Grid",
        asset_type="grid",
        criticality=0.9,
    )
    asset_b = Asset(
        name="Monitoring Dashboard",
        asset_type="monitoring",
        criticality=0.3,
    )

    db_session.add_all([asset_a, asset_b])
    db_session.commit()

    dependency = Dependency(
        source_asset_id=asset_a.id,
        target_asset_id=asset_b.id,
        dependency_type="network",
        strength=0.4,
    )

    db_session.add(dependency)
    db_session.commit()

    response = client.post(
        "/api/v1/failure-simulation/impact",
        json={
            "failed_asset_id": str(asset_a.id),
            "propagation_threshold": 0.7,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["failed_asset_id"] == str(asset_a.id)
    assert data["impacted_asset_count"] == 0
    assert data["impacted_assets"] == []


def test_failure_impact_api_rejects_invalid_threshold(client, db_session):
    asset = Asset(
        name="External Grid",
        asset_type="grid",
        criticality=0.9,
    )

    db_session.add(asset)
    db_session.commit()

    response = client.post(
        "/api/v1/failure-simulation/impact",
        json={
            "failed_asset_id": str(asset.id),
            "propagation_threshold": 1.5,
        },
    )

    assert response.status_code == 422