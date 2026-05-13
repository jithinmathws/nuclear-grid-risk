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

    impacted_asset_ids = {
        asset["asset_id"]
        for asset in impacted_assets
    }

    assert str(asset_b.id) in impacted_asset_ids
    assert str(asset_c.id) in impacted_asset_ids
    assert len(impacted_assets) == 2

    substation = next(
        asset for asset in impacted_assets
        if asset["asset_id"] == str(asset_b.id)
    )

    assert substation["caused_by_asset_id"] == str(asset_a.id)
    assert substation["dependency_type"] == "power"
    assert substation["propagation_strength"] == 1.0

    cooling_system = next(
        asset for asset in impacted_assets
        if asset["asset_id"] == str(asset_c.id)
    )

    assert cooling_system["caused_by_asset_id"] == str(asset_b.id)
    assert cooling_system["dependency_type"] == "power"
    assert cooling_system["propagation_strength"] == 1.0

def test_time_step_failure_respects_dependency_delay(db_session):
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

    service = FailureImpactService(db_session)

    timeline = service.simulate_time_step_failure(
        failed_asset_ids=[asset_a.id],
        propagation_threshold=0.7,
        max_time_minutes=60,
    )

    assert len(timeline) == 2

    initial_event = timeline[0]
    impacted_event = timeline[1]

    assert initial_event["asset_id"] == str(asset_a.id)
    assert initial_event["state"] == "failed"
    assert initial_event["time_minute"] == 0

    assert impacted_event["asset_id"] == str(asset_b.id)
    assert impacted_event["state"] == "failed"
    assert impacted_event["time_minute"] == 10
    assert impacted_event["caused_by_asset_id"] == str(asset_a.id)
    assert impacted_event["dependency_type"] == "power"
    assert impacted_event["propagation_strength"] == 1.0

def test_time_step_failure_accumulates_dependency_delays(db_session):
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
        failure_delay_minutes=10,
    )
    dependency_bc = Dependency(
        source_asset_id=asset_b.id,
        target_asset_id=asset_c.id,
        dependency_type="power",
        strength=1.0,
        failure_delay_minutes=20,
    )

    db_session.add_all([dependency_ab, dependency_bc])
    db_session.commit()

    service = FailureImpactService(db_session)

    timeline = service.simulate_time_step_failure(
        failed_asset_ids=[asset_a.id],
        propagation_threshold=0.7,
        max_time_minutes=60,
    )

    events_by_asset_id = {
        event["asset_id"]: event
        for event in timeline
    }

    assert len(timeline) == 3

    assert events_by_asset_id[str(asset_a.id)]["time_minute"] == 0
    assert events_by_asset_id[str(asset_a.id)]["state"] == "failed"

    assert events_by_asset_id[str(asset_b.id)]["time_minute"] == 10
    assert events_by_asset_id[str(asset_b.id)]["state"] == "failed"
    assert events_by_asset_id[str(asset_b.id)]["caused_by_asset_id"] == str(asset_a.id)

    assert events_by_asset_id[str(asset_c.id)]["time_minute"] == 30
    assert events_by_asset_id[str(asset_c.id)]["state"] == "failed"
    assert events_by_asset_id[str(asset_c.id)]["caused_by_asset_id"] == str(asset_b.id)

def test_time_step_failure_does_not_schedule_weak_dependency(db_session):
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
        failure_delay_minutes=10,
    )

    db_session.add(dependency)
    db_session.commit()

    service = FailureImpactService(db_session)

    timeline = service.simulate_time_step_failure(
        failed_asset_ids=[asset_a.id],
        propagation_threshold=0.7,
        max_time_minutes=60,
    )

    event_asset_ids = {
        event["asset_id"]
        for event in timeline
    }

    assert str(asset_a.id) in event_asset_ids
    assert str(asset_b.id) not in event_asset_ids
    assert len(timeline) == 1

def test_time_step_failure_marks_medium_strength_dependency_as_degraded(db_session):
    asset_a = Asset(
        name="External Grid",
        asset_type="grid",
        criticality=0.9,
    )
    asset_b = Asset(
        name="Monitoring System",
        asset_type="monitoring",
        criticality=0.5,
    )

    db_session.add_all([asset_a, asset_b])
    db_session.commit()

    dependency = Dependency(
        source_asset_id=asset_a.id,
        target_asset_id=asset_b.id,
        dependency_type="network",
        strength=0.6,
        failure_delay_minutes=5,
    )

    db_session.add(dependency)
    db_session.commit()

    service = FailureImpactService(db_session)

    timeline = service.simulate_time_step_failure(
        failed_asset_ids=[asset_a.id],
        propagation_threshold=0.5,
        max_time_minutes=60,
    )

    events_by_asset_id = {
        event["asset_id"]: event
        for event in timeline
    }

    assert events_by_asset_id[str(asset_a.id)]["state"] == "failed"
    assert events_by_asset_id[str(asset_b.id)]["state"] == "degraded"
    assert events_by_asset_id[str(asset_b.id)]["time_minute"] == 5

def test_time_step_failure_does_not_propagate_when_redundant_dependency_is_active(db_session):
    grid_a = Asset(
        name="Grid A",
        asset_type="grid",
        criticality=0.9,
    )
    grid_b = Asset(
        name="Grid B",
        asset_type="grid",
        criticality=0.9,
    )
    cooling_system = Asset(
        name="Cooling System",
        asset_type="cooling",
        criticality=1.0,
    )

    db_session.add_all([grid_a, grid_b, cooling_system])
    db_session.commit()

    dependency_a = Dependency(
        source_asset_id=grid_a.id,
        target_asset_id=cooling_system.id,
        dependency_type="power",
        strength=1.0,
        failure_delay_minutes=10,
        redundancy_group="external_power",
    )
    dependency_b = Dependency(
        source_asset_id=grid_b.id,
        target_asset_id=cooling_system.id,
        dependency_type="power",
        strength=1.0,
        failure_delay_minutes=10,
        redundancy_group="external_power",
    )

    db_session.add_all([dependency_a, dependency_b])
    db_session.commit()

    service = FailureImpactService(db_session)

    timeline = service.simulate_time_step_failure(
        failed_asset_ids=[grid_a.id],
        propagation_threshold=0.7,
        max_time_minutes=60,
    )

    event_asset_ids = {
        event["asset_id"]
        for event in timeline
    }

    assert str(grid_a.id) in event_asset_ids
    assert str(cooling_system.id) not in event_asset_ids
    assert len(timeline) == 1

def test_time_step_failure_propagates_when_all_redundant_dependencies_fail(db_session):
    grid_a = Asset(
        name="Grid A",
        asset_type="grid",
        criticality=0.9,
    )
    grid_b = Asset(
        name="Grid B",
        asset_type="grid",
        criticality=0.9,
    )
    cooling_system = Asset(
        name="Cooling System",
        asset_type="cooling",
        criticality=1.0,
    )

    db_session.add_all([grid_a, grid_b, cooling_system])
    db_session.commit()

    dependency_a = Dependency(
        source_asset_id=grid_a.id,
        target_asset_id=cooling_system.id,
        dependency_type="power",
        strength=1.0,
        failure_delay_minutes=10,
        redundancy_group="external_power",
    )
    dependency_b = Dependency(
        source_asset_id=grid_b.id,
        target_asset_id=cooling_system.id,
        dependency_type="power",
        strength=1.0,
        failure_delay_minutes=10,
        redundancy_group="external_power",
    )

    db_session.add_all([dependency_a, dependency_b])
    db_session.commit()

    service = FailureImpactService(db_session)

    timeline = service.simulate_time_step_failure(
        failed_asset_ids=[grid_a.id, grid_b.id],
        propagation_threshold=0.7,
        max_time_minutes=60,
    )

    events_by_asset_id = {
        event["asset_id"]: event
        for event in timeline
    }

    assert str(grid_a.id) in events_by_asset_id
    assert str(grid_b.id) in events_by_asset_id
    assert str(cooling_system.id) in events_by_asset_id

    assert events_by_asset_id[str(grid_a.id)]["time_minute"] == 0
    assert events_by_asset_id[str(grid_b.id)]["time_minute"] == 0
    assert events_by_asset_id[str(cooling_system.id)]["time_minute"] == 10
    assert events_by_asset_id[str(cooling_system.id)]["state"] == "failed"