import os
import uuid

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client() -> TestClient:
    db_path = f"/tmp/test_{uuid.uuid4().hex}.db"
    os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{db_path}"

    from backend.api.main import create_app

    app = create_app()
    with TestClient(app) as test_client:
        yield test_client
