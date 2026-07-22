# Task Tracker API — Module 1

A learning-project REST API built with **Python + FastAPI**, following ADR-001:
layered architecture (routes → services → schemas → JSON file storage) with a
local `tasks.json` file as the persistence layer (added in later steps).

This skeleton currently exposes a single `GET /health` endpoint.

## Requirements

- Python 3.11+ (3.10 works too)

## Setup

```bash
# 1. Create and activate a virtual environment
python -m venv venv

# Linux/macOS
source venv/bin/activate
# Windows PowerShell
.\venv\Scripts\Activate.ps1

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create your local environment file
cp .env.example .env        # PowerShell: Copy-Item .env.example .env
```

## Run the server

```bash
uvicorn app.main:app --reload --port 8000
```

The backend will be available at http://127.0.0.1:8000.

## Open the frontend

The frontend is a plain static HTML app in `frontend/index.html`.

Option 1: open `frontend/index.html` directly in your browser.

Option 2: serve the frontend from a simple local server and open the page at `http://127.0.0.1:5500`:

```bash
cd frontend
python -m http.server 5500
```

The frontend expects the backend to be running at `http://127.0.0.1:8000`.

## Run tests

From the project root run:

```bash
pytest -q
```

## Test the health endpoint

```bash
curl http://127.0.0.1:8000/health
```

Expected response shape:

```json
{ "status": "ok", "timestamp": "2026-07-12T08:30:00.000000+00:00" }
```

## API docs (Swagger)

Open in your browser: <http://127.0.0.1:8000/docs>