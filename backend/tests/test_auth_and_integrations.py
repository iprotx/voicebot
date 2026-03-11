import uuid


def _register_and_get_token(client, email: str | None = None) -> str:
    identity = email or f"admin_{uuid.uuid4().hex[:8]}@example.com"
    res = client.post(
        "/auth/register",
        json={"email": identity, "password": "StrongPass123"},
    )
    assert res.status_code == 200
    return res.json()["access_token"]


def test_admin_login(client) -> None:
    email = f"admin_{uuid.uuid4().hex[:8]}@example.com"
    _register_and_get_token(client, email=email)
    login = client.post(
        "/auth/login",
        json={"email": email, "password": "StrongPass123"},
    )
    assert login.status_code == 200
    assert "access_token" in login.json()


def test_integration_crud_lite(client) -> None:
    token = _register_and_get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    create = client.post(
        "/integrations",
        json={"name": "Primary Userbot", "kind": "userbot", "api_id": "123", "api_hash": "abc"},
        headers=headers,
    )
    assert create.status_code == 200
    integration_id = create.json()["id"]

    listing = client.get("/integrations", headers=headers)
    assert listing.status_code == 200
    assert len(listing.json()) >= 1

    deactivate = client.patch(f"/integrations/{integration_id}/deactivate", headers=headers)
    assert deactivate.status_code == 200
    assert deactivate.json()["is_active"] is False


def test_integrations_unauthorized(client) -> None:
    response = client.get("/integrations")
    assert response.status_code == 403
