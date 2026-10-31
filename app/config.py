"""Application configuration loaded from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

# Load local development settings when a .env file is present.
load_dotenv()


HARD_MAX_ITERATIONS = 10_000_000


def _read_int(name: str, default: int) -> int:
    raw_value = os.getenv(name)
    if raw_value is None or raw_value == "":
        return default
    try:
        return int(raw_value)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer; received {raw_value!r}") from exc


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "AutoScaleLab")
    app_env: str = os.getenv("APP_ENV", "development")
    app_version: str = os.getenv("APP_VERSION", "0.1.0-dev")
    instance_id: str = os.getenv("INSTANCE_ID", "local")
    log_level: str = os.getenv("LOG_LEVEL", "INFO").upper()
    port: int = _read_int("PORT", 8000)
    default_iterations: int = _read_int("DEFAULT_ITERATIONS", 250_000)
    max_iterations: int = _read_int("MAX_ITERATIONS", 2_000_000)

    def validate(self) -> None:
        if not 1 <= self.port <= 65535:
            raise ValueError("PORT must be between 1 and 65535")
        if self.log_level not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
            raise ValueError("LOG_LEVEL must be DEBUG, INFO, WARNING, ERROR, or CRITICAL")
        if not 1 <= self.max_iterations <= HARD_MAX_ITERATIONS:
            raise ValueError(
                f"MAX_ITERATIONS must be between 1 and {HARD_MAX_ITERATIONS:,}"
            )
        if not 1 <= self.default_iterations <= self.max_iterations:
            raise ValueError("DEFAULT_ITERATIONS must be between 1 and MAX_ITERATIONS")


settings = Settings()
settings.validate()
