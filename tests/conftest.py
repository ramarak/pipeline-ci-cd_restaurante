import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.store import reset


@pytest.fixture
def client():
    reset()
    return TestClient(app)


@pytest.fixture
def admin_headers():
    return {"Authorization": "Bearer token-admin"}
