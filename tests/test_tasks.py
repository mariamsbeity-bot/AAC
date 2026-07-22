"""Module 2 tests: CRUD, filtering, and status-transition rules."""

from datetime import date, datetime, timedelta, timezone

from fastapi.testclient import TestClient

PAST_DATE = "2020-01-01"
FUTURE_DATE = (date.today() + timedelta(days=30)).isoformat()

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


def test_list_tasks_overdue_filter_returns_only_overdue(client: TestClient):
    utc_today = datetime.now(timezone.utc).date()
    yesterday = (utc_today - timedelta(days=1)).isoformat()
    tomorrow = (utc_today + timedelta(days=1)).isoformat()

    overdue_task = client.post(
        "/tasks",
        json={"title": "Overdue task", "due_date": yesterday},
    )
    assert overdue_task.status_code == 201

    completed_late_task = client.post(
        "/tasks",
        json={"title": "Completed late", "status": "Done", "due_date": yesterday},
    )
    assert completed_late_task.status_code == 201

    future_task = client.post(
        "/tasks",
        json={"title": "Future task", "due_date": tomorrow},
    )
    assert future_task.status_code == 201

    response = client.get("/tasks", params={"overdue": "true"})
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["id"] == overdue_task.json()["id"]
    assert body[0]["due_state"] == "overdue"
    assert body[0]["due_date"] == yesterday


def test_create_task_with_valid_due_date_returns_201_and_echoes_date(client: TestClient):
    response = client.post(
        "/tasks",
        json={"title": "Task with due date", "due_date": FUTURE_DATE},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["due_date"] == FUTURE_DATE
    assert body["due_state"] is None


def test_create_task_without_due_date_returns_201_with_null_due_date(client: TestClient):
    response = client.post("/tasks", json={"title": "Task without due date"})
    assert response.status_code == 201
    body = response.json()
    assert body["due_date"] is None
    assert body["due_state"] is None


def test_create_task_invalid_due_date_format_returns_422_naming_due_date(client: TestClient):
    response = client.post(
        "/tasks",
        json={"title": "Bad due date", "due_date": "banana"},
    )
    assert response.status_code == 422
    body = response.json()
    assert isinstance(body["detail"], list)
    assert any(err["loc"][-1] == "due_date" for err in body["detail"])


def test_past_due_date_not_done_has_due_state_overdue(client: TestClient):
    response = client.post(
        "/tasks",
        json={"title": "Past due task", "due_date": PAST_DATE},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["due_date"] == PAST_DATE
    assert body["status"] == "ToDo"
    assert body["due_state"] == "overdue"


def test_past_due_date_done_has_due_state_completed_late(client: TestClient):
    create_response = client.post(
        "/tasks",
        json={"title": "Completed late task", "due_date": PAST_DATE},
    )
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    patch_response = client.patch(f"/tasks/{task_id}", json={"status": "InProgress"})
    assert patch_response.status_code == 200
    assert patch_response.json()["status"] == "InProgress"

    final_response = client.patch(f"/tasks/{task_id}", json={"status": "Done"})
    assert final_response.status_code == 200
    body = final_response.json()
    assert body["status"] == "Done"
    assert body["due_date"] == PAST_DATE
    assert body["due_state"] == "completed_late"


def test_patch_due_date_updates_value(client: TestClient):
    create_response = client.post("/tasks", json={"title": "Set due date later"})
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    update_response = client.patch(
        f"/tasks/{task_id}",
        json={"due_date": FUTURE_DATE},
    )
    assert update_response.status_code == 200
    body = update_response.json()
    assert body["due_date"] == FUTURE_DATE
    assert body["due_state"] is None


def test_patch_due_date_null_clears_value(client: TestClient):
    create_response = client.post(
        "/tasks",
        json={"title": "Clear due date", "due_date": FUTURE_DATE},
    )
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    update_response = client.patch(
        f"/tasks/{task_id}",
        json={"due_date": None},
    )
    assert update_response.status_code == 200
    body = update_response.json()
    assert body["due_date"] is None
    assert body["due_state"] is None


def test_patch_without_due_date_leaves_existing_date_unchanged(client: TestClient):
    create_response = client.post(
        "/tasks",
        json={"title": "Keep due date", "due_date": FUTURE_DATE},
    )
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    update_response = client.patch(
        f"/tasks/{task_id}",
        json={"title": "new title"},
    )
    assert update_response.status_code == 200
    body = update_response.json()
    assert body["title"] == "new title"
    assert body["due_date"] == FUTURE_DATE


def test_overdue_filter_excludes_completed_late_and_future_tasks(client: TestClient):
    overdue_task = client.post(
        "/tasks",
        json={"title": "Overdue only", "due_date": PAST_DATE},
    )
    assert overdue_task.status_code == 201
    overdue_id = overdue_task.json()["id"]

    completed_late_task = client.post(
        "/tasks",
        json={"title": "Completed late task", "due_date": PAST_DATE},
    )
    assert completed_late_task.status_code == 201
    completed_id = completed_late_task.json()["id"]

    client.patch(f"/tasks/{completed_id}", json={"status": "InProgress"})
    done_response = client.patch(f"/tasks/{completed_id}", json={"status": "Done"})
    assert done_response.status_code == 200
    assert done_response.json()["due_state"] == "completed_late"

    future_task = client.post(
        "/tasks",
        json={"title": "Future task", "due_date": FUTURE_DATE},
    )
    assert future_task.status_code == 201

    no_date_task = client.post(
        "/tasks",
        json={"title": "No due date task"},
    )
    assert no_date_task.status_code == 201

    response = client.get("/tasks", params={"overdue": "true"})
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["id"] == overdue_id
    assert body[0]["due_state"] == "overdue"


def test_overdue_filter_no_matches_returns_200_empty_list(client: TestClient):
    future_task = client.post(
        "/tasks",
        json={"title": "Future task only", "due_date": FUTURE_DATE},
    )
    assert future_task.status_code == 201

    response = client.get("/tasks", params={"overdue": "true"})
    assert response.status_code == 200
    assert response.json() == []


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