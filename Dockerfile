# ---- Build stage: resolve and install Python dependencies ----
FROM python:3.11-slim AS builder

WORKDIR /build

COPY requirements.txt .

RUN pip install --no-cache-dir --user -r requirements.txt

# ---- Runtime stage: minimal image with only what's needed to run the app ----
FROM python:3.11-slim AS runtime

RUN groupadd --system app && useradd --system --gid app --no-create-home app

WORKDIR /app

COPY --from=builder /root/.local /home/app/.local
COPY app/ ./app/
COPY requirements.txt .

RUN chown -R app:app /app /home/app/.local

ENV PATH=/home/app/.local/bin:$PATH \
    PYTHONUNBUFFERED=1

USER app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
