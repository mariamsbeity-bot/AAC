"""Application configuration loaded from environment variables."""

import os

from dotenv import load_dotenv

# Load variables from a .env file if present
load_dotenv()

APP_ENV: str = os.getenv("APP_ENV", "development")
PORT: int = int(os.getenv("PORT", "8000"))