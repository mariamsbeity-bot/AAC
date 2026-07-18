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