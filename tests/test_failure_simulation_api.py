from app.models.asset import Asset
from app.models.dependency import Dependency
from app.services.failure_impact_service import FailureImpactService


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

def test_failure_impact_propagates_when_strength_meets_threshold(db_session):
    asset_a = Asset(
        name="External Grid",
        asset_type="grid",
        criticality=0.9,
    )

    asset_b = Asset(
        name="Cooling System",
        asset_type="cooling",
        criticality=1.0,
    )

    db_session.add_all([asset_a, asset_b])
    db_session.commit()

    dependency = Dependency(
        source_asset_id=asset_a.id,
        target_asset_id=asset_b.id,
        dependency_type="power",
        strength=0.9,
    )

    db_session.add(dependency)
    db_session.commit()

    service = FailureImpactService(db_session)

    impacted_assets = service.get_downstream_impact(
        failed_asset_id=asset_a.id,
        propagation_threshold=0.7,
    )

    impacted_asset_ids = {
        asset["asset_id"]
        for asset in impacted_assets
    }

    assert str(asset_b.id) in impacted_asset_ids
    assert len(impacted_assets) == 1

def test_failure_impact_does_not_propagate_when_strength_below_threshold(db_session):
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

    service = FailureImpactService(db_session)

    impacted_assets = service.get_downstream_impact(
        failed_asset_id=asset_a.id,
        propagation_threshold=0.7,
    )

    impacted_asset_ids = {
        asset["asset_id"]
        for asset in impacted_assets
    }

    assert str(asset_b.id) not in impacted_asset_ids
    assert len(impacted_assets) == 0

def test_failure_impact_stops_at_weak_dependency(db_session):
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

    asset_c = Asset(
        name="Monitoring Dashboard",
        asset_type="monitoring",
        criticality=0.3,
    )

    db_session.add_all([asset_a, asset_b, asset_c])
    db_session.commit()

    dependency_ab = Dependency(
        source_asset_id=asset_a.id,
        target_asset_id=asset_b.id,
        dependency_type="power",
        strength=0.9,
    )

    dependency_bc = Dependency(
        source_asset_id=asset_b.id,
        target_asset_id=asset_c.id,
        dependency_type="network",
        strength=0.3,
    )

    db_session.add_all([dependency_ab, dependency_bc])
    db_session.commit()

    service = FailureImpactService(db_session)

    impacted_assets = service.get_downstream_impact(
        failed_asset_id=asset_a.id,
        propagation_threshold=0.7,
    )

    impacted_asset_ids = {
        asset["asset_id"]
        for asset in impacted_assets
    }

    assert str(asset_b.id) in impacted_asset_ids
    assert str(asset_c.id) not in impacted_asset_ids

    assert len(impacted_assets) == 1