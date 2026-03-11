import uuid


def _admin_headers(client) -> dict[str, str]:
    email = f"risk_admin_{uuid.uuid4().hex[:8]}@example.com"
    res = client.post("/auth/register", json={"email": email, "password": "StrongPass123"})
    assert res.status_code == 200
    return {"Authorization": f"Bearer {res.json()['access_token']}"}


def test_risk_score_and_alert_generation(client) -> None:
    headers = _admin_headers(client)

    user_res = client.post("/users", json={"telegram_id": 9991, "username": "suspect"})
    user_id = user_res.json()["id"]

    risk_payload = {
        "user_id": user_id,
        "style_similarity": 0.98,
        "activity_overlap": 0.95,
        "scam_pattern_score": 0.95,
    }
    created = client.post("/risk/score", json=risk_payload, headers=headers)
    assert created.status_code == 200
    assert created.json()["risk_score"] > 70

    history = client.get(f"/risk/users/{user_id}", headers=headers)
    assert history.status_code == 200
    assert len(history.json()) == 1

    alerts = client.get(f"/risk/users/{user_id}/alerts", headers=headers)
    assert alerts.status_code == 200
    assert len(alerts.json()) == 3


def test_risk_endpoint_requires_auth(client) -> None:
    response = client.get("/risk/users/1")
    assert response.status_code == 403
