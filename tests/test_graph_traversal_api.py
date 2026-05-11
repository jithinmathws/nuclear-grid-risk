from app.models.asset import Asset
from app.models.dependency import Dependency


def test_get_upstream_assets_api(client, db_session):
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

    response = client.get(f"/api/v1/graph/{control_center.id}/upstream")

    assert response.status_code == 200

    data = response.json()

    assert data["asset_id"] == str(control_center.id)
    assert set(data["upstream_assets"]) == {
        str(plant.id),
        str(substation.id),
    }


def test_get_downstream_assets_api(client, db_session):
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

    response = client.get(f"/api/v1/graph/{plant.id}/downstream")

    assert response.status_code == 200

    data = response.json()

    assert data["asset_id"] == str(plant.id)
    assert set(data["downstream_assets"]) == {
        str(substation.id),
        str(control_center.id),
    }


def test_check_path_exists_api(client, db_session):
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

    db_session.add_all([plant, substation])
    db_session.commit()

    db_session.refresh(plant)
    db_session.refresh(substation)

    dependency = Dependency(
        source_asset_id=plant.id,
        target_asset_id=substation.id,
        dependency_type="POWER_FLOW",
        strength=0.90,
    )

    db_session.add(dependency)
    db_session.commit()

    response = client.get(
        "/api/v1/graph/path/check",
        params={
            "source_asset_id": str(plant.id),
            "target_asset_id": str(substation.id),
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["source_asset_id"] == str(plant.id)
    assert data["target_asset_id"] == str(substation.id)
    assert data["path_exists"] is True


def test_get_shortest_path_api(client, db_session):
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

    response = client.get(
        "/api/v1/graph/path/shortest",
        params={
            "source_asset_id": str(plant.id),
            "target_asset_id": str(control_center.id),
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["path"] == [
        str(plant.id),
        str(substation.id),
        str(control_center.id),
    ]
    assert data["path_length"] == 3