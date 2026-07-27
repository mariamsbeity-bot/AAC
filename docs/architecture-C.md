# Architecture C: Task Tracker

## 1. What the app does
The Task Tracker is a FastAPI-based API for managing tasks and task comments. Its visible behavior includes task creation, listing, retrieval, updating, deletion, comment creation/listing/deletion, and a health endpoint.

## 2. Data model
The visible entities are Tasks and Comments. Task data includes id, title, description, status, priority, assignee, due_date, created_at, and updated_at. Task status values are ToDo, InProgress, and Done; task priority values are Low, Medium, and High. A computed field named due_state is exposed on task responses and is derived from the current UTC date and the task’s due_date/status. Comment data includes id, task_id, text, and created_at.

## 3. Request flow
When a user creates a task, the API receives a POST request to /tasks with a task payload. The request model validates the payload, rejects unknown fields, trims and checks the title, and applies default values for fields such as status and priority. The storage layer creates a task object with a generated id and UTC timestamps, stores it in memory, and returns the created task in the response body.

## 4. Key files
- [app/main.py](../app/main.py) — Defines the FastAPI routes for task and comment operations, health, and local CORS behavior.
- [app/models.py](../app/models.py) — Defines the request/response models, enums, validation rules, and computed due_state.
- [app/storage.py](../app/storage.py) — Implements task creation, lookup, update, deletion, and in-memory storage.
- [app/comments_storage.py](../app/comments_storage.py) — Implements comment persistence helpers used by the API layer.
- [app/business_rules.py](../app/business_rules.py) — Implements the allowed task status transition rules used during updates.
- [app/api/routes/health.py](../app/api/routes/health.py) — Provides the health route included by the API entry point.
- [app/core/config.py](../app/core/config.py) — Supplies APP_ENV used by the root endpoint.

## 5. Conventions
Validation is enforced in the request models: titles and comments are trimmed and must not be blank, unknown fields are rejected, and invalid enum values are not accepted. Storage is in-memory rather than persistent; task data is held in a dictionary and cleared through a reset helper used by tests. Error handling is explicit in the API layer: missing tasks or comments return 404, and invalid input or invalid status transitions return 422. The code shows CORS configuration for local development and indicates that the API is intended to be called by a separate client, but the frontend implementation itself is not visible from the files I read.

## 6. Not visible or assumptions
The frontend implementation is not visible from the files I read. Deployment, authentication, persistence beyond in-memory storage, and detailed runtime configuration are not visible from the files I read.
