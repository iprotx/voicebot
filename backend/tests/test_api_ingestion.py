from datetime import datetime, timezone


def test_users_and_messages_flow(client) -> None:
    user_payload = {"telegram_id": 1001, "username": "alice", "display_name": "Alice", "language": "en"}
    user_res = client.post("/users", json=user_payload)
    assert user_res.status_code == 200
    user_id = user_res.json()["id"]

    read_user = client.get(f"/users/{user_id}")
    assert read_user.status_code == 200
    assert read_user.json()["telegram_id"] == 1001

    ts = datetime.now(timezone.utc).isoformat()
    msg_payload = {
        "message_id": 1,
        "user_id": user_id,
        "chat_id": 200,
        "timestamp": ts,
        "text": "hello world",
        "reply_to": None,
        "username": "alice",
        "display_name": "Alice",
    }
    msg_res = client.post("/messages", json=msg_payload)
    assert msg_res.status_code == 200
    message_row_id = msg_res.json()["id"]

    get_msg = client.get(f"/messages/{message_row_id}")
    assert get_msg.status_code == 200
    assert get_msg.json()["message_id"] == 1


def test_batch_ingestion(client) -> None:
    user = client.post("/users", json={"telegram_id": 2002}).json()
    ts = datetime.now(timezone.utc).isoformat()
    payload = {
        "messages": [
            {
                "message_id": 10,
                "user_id": user["id"],
                "chat_id": 1,
                "timestamp": ts,
                "text": "buy now",
            },
            {
                "message_id": 11,
                "user_id": user["id"],
                "chat_id": 1,
                "timestamp": ts,
                "text": "limited offer",
            },
        ]
    }
    response = client.post("/messages/batch", json=payload)
    assert response.status_code == 200
    assert len(response.json()) == 2
