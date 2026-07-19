"""Module 2 tests: CRUD, filtering, and status-transition rules."""

from fastapi.testclient import TestClient

# ---------------------------------------------------------------------------
# POST /tasks
# ---------------------------------------------------------------------------


def test_create_task_valid_returns_201_with_full_body(client: TestClient):
    response = client.post(
        "/tasks",
        json={"title": "Write tests", "priority": "High"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Write tests"
    assert body["description"] == ""
    assert body["status"] == "ToDo"
    assert body["priority"] == "High"
    assert body["assignee"] is None
    assert body["id"]
    assert body["created_at"]
    assert body["updated_at"]


def test_create_task_missing_title_returns_422(client: TestClient):
    response = client.post("/tasks", json={})
    assert response.status_code == 422


def test_create_task_blank_title_returns_422(client: TestClient):
    response = client.post("/tasks", json={"title": "   "})
    assert response.status_code == 422


def test_create_task_invalid_priority_returns_422(client: TestClient):
    response = client.post(
        "/tasks",
        json={"title": "Bad priority", "priority": "Critical"},
    )
    assert response.status_code == 422


def test_create_task_unknown_field_returns_422(client: TestClient):
    response = client.post(
        "/tasks",
        json={"title": "Extra field", "nickname": "x"},
    )
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# GET /tasks
# ---------------------------------------------------------------------------


def test_list_tasks_empty_returns_200_and_empty_list(client: TestClient):
    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == []


def test_list_tasks_filter_by_status_no_match_returns_200_and_empty_list(
    client: TestClient, created_task: dict
):
    response = client.get("/tasks", params={"status": "Done"})
    assert response.status_code == 200
    assert response.json() == []


def test_list_tasks_filter_by_priority_returns_only_matches(client: TestClient):
    r_high = client.post("/tasks", json={"title": "High one", "priority": "High"})
    assert r_high.status_code == 201
    r_low = client.post("/tasks", json={"title": "Low one", "priority": "Low"})
    assert r_low.status_code == 201

    response = client.get("/tasks", params={"priority": "High"})
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["id"] == r_high.json()["id"]
    assert body[0]["priority"] == "High"


# ---------------------------------------------------------------------------
# GET /tasks/{task_id}
# ---------------------------------------------------------------------------


def test_get_task_by_id_returns_task(client: TestClient, created_task: dict):
    task_id = created_task["id"]
    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json() == created_task


def test_get_task_by_id_not_found_returns_404_with_detail(client: TestClient):
    response = client.get("/tasks/nonexistent-id")
    assert response.status_code == 404
    assert response.json()["detail"] == "Task with id nonexistent-id not found"


# ---------------------------------------------------------------------------
# PATCH /tasks/{task_id}
# ---------------------------------------------------------------------------


def test_patch_partial_update_keeps_other_fields(
    client: TestClient, created_task: dict
):
    task_id = created_task["id"]
    response = client.patch(f"/tasks/{task_id}", json={"title": "Renamed"})
    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "Renamed"
    assert body["description"] == created_task["description"]
    assert body["status"] == created_task["status"]
    assert body["priority"] == created_task["priority"]
    assert body["assignee"] == created_task["assignee"]
    assert body["created_at"] == created_task["created_at"]


def test_patch_not_found_returns_404(client: TestClient):
    response = client.patch("/tasks/nonexistent-id", json={"title": "Ghost"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Task with id nonexistent-id not found"


def test_patch_valid_transition_todo_to_inprogress_returns_200(
    client: TestClient, created_task: dict
):
    task_id = created_task["id"]
    response = client.patch(f"/tasks/{task_id}", json={"status": "InProgress"})
    assert response.status_code == 200
    assert response.json()["status"] == "InProgress"


def test_patch_invalid_transition_todo_to_done_returns_422(
    client: TestClient, created_task: dict
):
    task_id = created_task["id"]
    response = client.patch(f"/tasks/{task_id}", json={"status": "Done"})
    assert response.status_code == 422
    assert "Invalid status transition" in response.json()["detail"]


def test_patch_same_status_returns_422(client: TestClient, created_task: dict):
    task_id = created_task["id"]
    response = client.patch(f"/tasks/{task_id}", json={"status": "ToDo"})
    assert response.status_code == 422
    assert "Invalid status transition" in response.json()["detail"]


def test_patch_invalid_priority_returns_422(client: TestClient):
    create_response = client.post(
        "/tasks",
        json={"title": "Update priority", "priority": "High"},
    )
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    response = client.patch(f"/tasks/{task_id}", json={"priority": "Critical"})

    assert response.status_code == 422
    body = response.json()
    assert isinstance(body["detail"], list)
    assert any(err["loc"][-1] == "priority" for err in body["detail"])
    assert any(
        err.get("type") == "enum"
        and "Input should be" in err.get("msg", "")
        and "Low" in err.get("msg", "")
        and "Medium" in err.get("msg", "")
        and "High" in err.get("msg", "")
        for err in body["detail"]
    )


# ---------------------------------------------------------------------------
# DELETE /tasks/{task_id}
# ---------------------------------------------------------------------------


def test_delete_existing_returns_204_no_body(client: TestClient, created_task: dict):
    task_id = created_task["id"]
    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 204
    assert response.content == b""

    follow_up = client.get(f"/tasks/{task_id}")
    assert follow_up.status_code == 404


def test_delete_missing_returns_404(client: TestClient):
    response = client.delete("/tasks/nonexistent-id")
    assert response.status_code == 404
    assert response.json()["detail"] == "Task with id nonexistent-id not found"