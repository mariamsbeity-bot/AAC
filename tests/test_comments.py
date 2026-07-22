from datetime import datetime, timezone, timedelta, date

from fastapi.testclient import TestClient

from app.comments_storage import get_comments_by_task


def test_create_comment_for_existing_task_returns_201(client: TestClient):
    task_response = client.post("/tasks", json={"title": "Task with comment"})
    assert task_response.status_code == 201
    task_id = task_response.json()["id"]

    response = client.post(
        f"/tasks/{task_id}/comments",
        json={"text": "This is a comment."},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["task_id"] == task_id
    assert body["text"] == "This is a comment."
    assert body["id"]
    assert body["created_at"]


def test_create_comment_blank_text_returns_422_naming_text(client: TestClient):
    task_response = client.post("/tasks", json={"title": "Task with invalid comment"})
    assert task_response.status_code == 201
    task_id = task_response.json()["id"]

    response = client.post(
        f"/tasks/{task_id}/comments",
        json={"text": "   "},
    )

    assert response.status_code == 422
    body = response.json()
    assert isinstance(body["detail"], list)
    assert any(err["loc"][-1] == "text" for err in body["detail"])


def test_create_comment_for_missing_task_returns_404(client: TestClient):
    response = client.post(
        "/tasks/nonexistent/comments",
        json={"text": "Hello"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Task with id nonexistent not found"


def test_list_comments_returns_200_and_empty_list_for_task_with_no_comments(client: TestClient):
    task_response = client.post("/tasks", json={"title": "Task with no comments"})
    assert task_response.status_code == 201
    task_id = task_response.json()["id"]

    response = client.get(f"/tasks/{task_id}/comments")
    assert response.status_code == 200
    assert response.json() == []


def test_list_comments_for_missing_task_returns_404(client: TestClient):
    response = client.get("/tasks/nonexistent/comments")
    assert response.status_code == 404
    assert response.json()["detail"] == "Task with id nonexistent not found"


def test_list_comments_returns_comments_sorted_by_creation_time(client: TestClient):
    task_response = client.post("/tasks", json={"title": "Task with multiple comments"})
    assert task_response.status_code == 201
    task_id = task_response.json()["id"]

    first = client.post(
        f"/tasks/{task_id}/comments",
        json={"text": "First comment"},
    )
    second = client.post(
        f"/tasks/{task_id}/comments",
        json={"text": "Second comment"},
    )

    assert first.status_code == 201
    assert second.status_code == 201

    response = client.get(f"/tasks/{task_id}/comments")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2
    assert body[0]["id"] == first.json()["id"]
    assert body[1]["id"] == second.json()["id"]


def test_delete_comment_returns_204_and_comment_is_removed(client: TestClient):
    task_response = client.post("/tasks", json={"title": "Task with deleteable comment"})
    assert task_response.status_code == 201
    task_id = task_response.json()["id"]

    comment_response = client.post(
        f"/tasks/{task_id}/comments",
        json={"text": "Comment to delete"},
    )
    assert comment_response.status_code == 201
    comment_id = comment_response.json()["id"]

    response = client.delete(f"/tasks/{task_id}/comments/{comment_id}")
    assert response.status_code == 204
    assert response.content == b""

    list_response = client.get(f"/tasks/{task_id}/comments")
    assert list_response.status_code == 200
    assert list_response.json() == []


def test_delete_comment_with_wrong_task_returns_404(client: TestClient):
    first_task = client.post("/tasks", json={"title": "First task"})
    second_task = client.post("/tasks", json={"title": "Second task"})
    assert first_task.status_code == 201
    assert second_task.status_code == 201
    first_id = first_task.json()["id"]
    second_id = second_task.json()["id"]

    comment_response = client.post(
        f"/tasks/{first_id}/comments",
        json={"text": "First task comment"},
    )
    assert comment_response.status_code == 201
    comment_id = comment_response.json()["id"]

    wrong_delete = client.delete(f"/tasks/{second_id}/comments/{comment_id}")
    assert wrong_delete.status_code == 404
    assert wrong_delete.json()["detail"] == f"Comment with id {comment_id} not found"


def test_delete_comment_for_missing_task_returns_404(client: TestClient):
    response = client.delete("/tasks/nonexistent/comments/some-comment-id")
    assert response.status_code == 404
    assert response.json()["detail"] == "Task with id nonexistent not found"


def test_delete_nonexistent_comment_returns_404(client: TestClient):
    task_response = client.post("/tasks", json={"title": "Task for missing comment"})
    assert task_response.status_code == 201
    task_id = task_response.json()["id"]

    response = client.delete(f"/tasks/{task_id}/comments/nonexistent-comment-id")
    assert response.status_code == 404
    assert response.json()["detail"] == "Comment with id nonexistent-comment-id not found"


def test_delete_task_cascades_comments(client: TestClient):
    task_response = client.post("/tasks", json={"title": "Task to delete with comments"})
    assert task_response.status_code == 201
    task_id = task_response.json()["id"]

    comment_response = client.post(
        f"/tasks/{task_id}/comments",
        json={"text": "Will be deleted with task"},
    )
    assert comment_response.status_code == 201

    delete_response = client.delete(f"/tasks/{task_id}")
    assert delete_response.status_code == 204

    assert get_comments_by_task(task_id) == []
