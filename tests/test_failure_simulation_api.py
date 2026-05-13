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

def test_time_step_failure_api_returns_timeline(client, db_session):
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
        failure_delay_minutes=10,
    )

    db_session.add(dependency)
    db_session.commit()

    response = client.post(
        "/api/v1/failure-simulation/time-step",
        json={
            "failed_asset_id": str(asset_a.id),
            "propagation_threshold": 0.7,
            "max_time_minutes": 60,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["failed_asset_id"] == str(asset_a.id)
    assert data["max_time_minutes"] == 60
    assert data["event_count"] == 2

    events_by_asset_id = {
        event["asset_id"]: event
        for event in data["timeline"]
    }

    assert events_by_asset_id[str(asset_a.id)]["state"] == "failed"
    assert events_by_asset_id[str(asset_a.id)]["time_minute"] == 0

    assert events_by_asset_id[str(asset_b.id)]["state"] == "failed"
    assert events_by_asset_id[str(asset_b.id)]["time_minute"] == 10
    assert events_by_asset_id[str(asset_b.id)]["caused_by_asset_id"] == str(asset_a.id)
    assert events_by_asset_id[str(asset_b.id)]["dependency_type"] == "power"
    assert events_by_asset_id[str(asset_b.id)]["propagation_strength"] == 1.0

    assert data["summary"]["failed_assets"] == 2
    assert data["summary"]["degraded_assets"] == 0
    assert data["summary"]["isolated_assets"] == 0
    assert data["summary"]["total_affected_assets"] == 2
    assert data["summary"]["max_impact_time_minute"] == 10