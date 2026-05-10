from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def create_test_asset(asset_type: str = "grid_node", criticality: int = 3) -> dict:
    payload = {
        "name": f"Asset-{uuid4()}",
        "asset_type": asset_type,
        "criticality": criticality,
        "status": "active",
    }

    response = client.post("/api/v1/assets/", json=payload)

    assert response.status_code == 201

    return response.json()


def create_test_dependency() -> dict:
    source_asset = create_test_asset(asset_type="nuclear_plant", criticality=5)
    target_asset = create_test_asset(asset_type="substation", criticality=4)

    payload = {
        "source_asset_id": source_asset["id"],
        "target_asset_id": target_asset["id"],
        "dependency_type": "power_flow",
        "strength": 0.85,
        "redundancy_group": "primary_grid",
        "common_mode_group": "regional_grid_failure",
        "failure_delay_minutes": 15,
        "extra_metadata": {
            "description": "Primary dependency from plant to substation",
        },
    }

    response = client.post("/api/v1/dependencies/", json=payload)

    assert response.status_code == 201

    return response.json()


def test_create_dependency():
    source_asset = create_test_asset(asset_type="nuclear_plant", criticality=5)
    target_asset = create_test_asset(asset_type="substation", criticality=4)

    payload = {
        "source_asset_id": source_asset["id"],
        "target_asset_id": target_asset["id"],
        "dependency_type": "power_flow",
        "strength": 0.85,
        "redundancy_group": "primary_grid",
        "common_mode_group": "regional_grid_failure",
        "failure_delay_minutes": 15,
        "extra_metadata": {
            "description": "Primary dependency from plant to substation",
        },
    }

    response = client.post("/api/v1/dependencies/", json=payload)

    assert response.status_code == 201

    data = response.json()

    assert data["id"] is not None
    assert data["source_asset_id"] == payload["source_asset_id"]
    assert data["target_asset_id"] == payload["target_asset_id"]
    assert data["dependency_type"] == payload["dependency_type"]
    assert data["strength"] == payload["strength"]
    assert data["redundancy_group"] == payload["redundancy_group"]
    assert data["common_mode_group"] == payload["common_mode_group"]
    assert data["failure_delay_minutes"] == payload["failure_delay_minutes"]
    assert data["extra_metadata"] == payload["extra_metadata"]


def test_list_dependencies():
    created_dependency = create_test_dependency()

    response = client.get("/api/v1/dependencies/")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert any(dependency["id"] == created_dependency["id"] for dependency in data)


def test_get_dependency_by_id():
    created_dependency = create_test_dependency()

    response = client.get(f"/api/v1/dependencies/{created_dependency['id']}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == created_dependency["id"]
    assert data["source_asset_id"] == created_dependency["source_asset_id"]
    assert data["target_asset_id"] == created_dependency["target_asset_id"]


def test_update_dependency():
    created_dependency = create_test_dependency()

    update_payload = {
        "strength": 0.45,
        "failure_delay_minutes": 30,
        "extra_metadata": {
            "description": "Updated dependency metadata",
        },
    }

    response = client.patch(f"/api/v1/dependencies/{created_dependency['id']}", json=update_payload)

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == created_dependency["id"]
    assert data["strength"] == update_payload["strength"]
    assert data["failure_delay_minutes"] == update_payload["failure_delay_minutes"]
    assert data["extra_metadata"] == update_payload["extra_metadata"]


def test_delete_dependency():
    created_dependency = create_test_dependency()

    delete_response = client.delete(f"/api/v1/dependencies/{created_dependency['id']}")

    assert delete_response.status_code == 204

    get_response = client.get(f"/api/v1/dependencies/{created_dependency['id']}")

    assert get_response.status_code == 404


def test_create_dependency_rejects_self_dependency():
    asset = create_test_asset(asset_type="substation", criticality=4)

    payload = {
        "source_asset_id": asset["id"],
        "target_asset_id": asset["id"],
        "dependency_type": "power_flow",
        "strength": 1.0,
        "failure_delay_minutes": 0,
        "extra_metadata": {},
    }

    response = client.post("/api/v1/dependencies/", json=payload)

    assert response.status_code == 400
    assert response.json()["detail"] == "Source and target assets must be different"


def test_create_dependency_rejects_missing_source_asset():
    target_asset = create_test_asset(asset_type="substation", criticality=4)

    payload = {
        "source_asset_id": str(uuid4()),
        "target_asset_id": target_asset["id"],
        "dependency_type": "power_flow",
        "strength": 1.0,
        "failure_delay_minutes": 0,
        "extra_metadata": {},
    }

    response = client.post("/api/v1/dependencies/", json=payload)

    assert response.status_code == 404
    assert response.json()["detail"] == "Asset not found"


def test_create_dependency_rejects_missing_target_asset():
    source_asset = create_test_asset(asset_type="nuclear_plant", criticality=5)

    payload = {
        "source_asset_id": source_asset["id"],
        "target_asset_id": str(uuid4()),
        "dependency_type": "power_flow",
        "strength": 1.0,
        "failure_delay_minutes": 0,
        "extra_metadata": {},
    }

    response = client.post("/api/v1/dependencies/", json=payload)

    assert response.status_code == 404
    assert response.json()["detail"] == "Asset not found"


def test_get_dependency_not_found():
    missing_dependency_id = uuid4()

    response = client.get(f"/api/v1/dependencies/{missing_dependency_id}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Dependency not found"

def test_create_dependency_rejects_duplicate_dependency():
    source_asset = create_test_asset(asset_type="nuclear_plant", criticality=5)
    target_asset = create_test_asset(asset_type="substation", criticality=4)

    payload = {
        "source_asset_id": source_asset["id"],
        "target_asset_id": target_asset["id"],
        "dependency_type": "power_flow",
        "strength": 0.85,
        "failure_delay_minutes": 15,
        "extra_metadata": {},
    }

    first_response = client.post("/api/v1/dependencies/", json=payload)
    assert first_response.status_code == 201

    second_response = client.post("/api/v1/dependencies/", json=payload)

    assert second_response.status_code == 409
    assert second_response.json()["detail"] == "Dependency already exists"