from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_asset():
    payload = {
        "name": f"Plant-{uuid4()}",
        "asset_type": "nuclear_plant",
        "criticality": 5,
        "status": "active",
    }

    response = client.post("/api/v1/assets/", json=payload)

    assert response.status_code == 201

    data = response.json()

    assert data["id"] is not None
    assert data["name"] == payload["name"]
    assert data["asset_type"] == payload["asset_type"]
    assert data["criticality"] == payload["criticality"]
    assert data["status"] == payload["status"]


def test_list_assets():
    payload = {
        "name": f"Grid-{uuid4()}",
        "asset_type": "grid_node",
        "criticality": 3,
        "status": "active",
    }

    create_response = client.post("/api/v1/assets/", json=payload)
    assert create_response.status_code == 201

    created_asset = create_response.json()

    response = client.get("/api/v1/assets/")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert any(asset["id"] == created_asset["id"] for asset in data)


def test_get_asset_by_id():
    payload = {
        "name": f"Substation-{uuid4()}",
        "asset_type": "substation",
        "criticality": 4,
        "status": "active",
    }

    create_response = client.post("/api/v1/assets/", json=payload)
    assert create_response.status_code == 201

    created_asset = create_response.json()

    response = client.get(f"/api/v1/assets/{created_asset['id']}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == created_asset["id"]
    assert data["name"] == payload["name"]


def test_update_asset():
    payload = {
        "name": f"Transmission-Line-{uuid4()}",
        "asset_type": "transmission_line",
        "criticality": 2,
        "status": "active",
    }

    create_response = client.post("/api/v1/assets/", json=payload)
    assert create_response.status_code == 201

    created_asset = create_response.json()

    update_payload = {
        "status": "maintenance",
        "criticality": 1,
    }

    response = client.patch(f"/api/v1/assets/{created_asset['id']}", json=update_payload)

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == created_asset["id"]
    assert data["status"] == "maintenance"
    assert data["criticality"] == 1
    assert data["name"] == payload["name"]


def test_delete_asset():
    payload = {
        "name": f"Backup-Diesel-{uuid4()}",
        "asset_type": "backup_generator",
        "criticality": 2,
        "status": "active",
    }

    create_response = client.post("/api/v1/assets/", json=payload)
    assert create_response.status_code == 201

    created_asset = create_response.json()

    delete_response = client.delete(f"/api/v1/assets/{created_asset['id']}")

    assert delete_response.status_code == 204

    get_response = client.get(f"/api/v1/assets/{created_asset['id']}")

    assert get_response.status_code == 404


def test_get_asset_not_found():
    missing_asset_id = uuid4()

    response = client.get(f"/api/v1/assets/{missing_asset_id}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Asset not found"