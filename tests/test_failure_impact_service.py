from app.models.asset import Asset
from app.models.dependency import Dependency
from app.services.failure_impact_service import FailureImpactService


def test_failure_impact_returns_all_downstream_assets(db_session):
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
        name="Cooling System",
        asset_type="cooling",
        criticality=1.0,
    )

    db_session.add_all([asset_a, asset_b, asset_c])
    db_session.commit()

    dependency_ab = Dependency(
        source_asset_id=asset_a.id,
        target_asset_id=asset_b.id,
        dependency_type="power",
        strength=1.0,
    )
    dependency_bc = Dependency(
        source_asset_id=asset_b.id,
        target_asset_id=asset_c.id,
        dependency_type="power",
        strength=1.0,
    )

    db_session.add_all([dependency_ab, dependency_bc])
    db_session.commit()

    service = FailureImpactService(db_session)

    impacted_assets = service.get_downstream_impact(asset_a.id)

    impacted_asset_ids = {asset["asset_id"] for asset in impacted_assets}

    assert str(asset_b.id) in impacted_asset_ids
    assert str(asset_c.id) in impacted_asset_ids
    assert len(impacted_assets) == 2