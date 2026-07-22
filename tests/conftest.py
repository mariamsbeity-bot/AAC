"""Shared pytest fixtures for the Task Tracker API tests."""

import pytest
from fastapi.testclient import TestClient

from app import storage
from app.comments_storage import _reset_comments
from app.main import app


@pytest.fixture(autouse=True)
def _reset_storage():
    """Clear the in-memory store before and after each test."""
    storage._reset()
    _reset_comments()
    yield
    storage._reset()
    _reset_comments()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def created_task(client: TestClient) -> dict:
    """Create a task via the API and return its response JSON."""
    response = client.post("/tasks", json={"title": "fixture task"})
    assert response.status_code == 201
    return response.json()