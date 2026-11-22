"""Configuration from environment variables."""

import os
from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class Settings:
    # repr=False keeps the connection string out of logs.
    database_url: str = field(repr=False)


def load_settings() -> Settings:
    database_url = os.environ.get("DATABASE_URL", "").strip()
    if not database_url:
        raise RuntimeError("DATABASE_URL is not set.")
    return Settings(database_url=database_url)
