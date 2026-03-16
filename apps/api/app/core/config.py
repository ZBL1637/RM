import os
from dataclasses import dataclass, field
from pathlib import Path


def get_allowed_origins() -> list[str]:
    configured_origins = os.getenv("ALLOWED_ORIGINS")

    if configured_origins:
        return [origin.strip() for origin in configured_origins.split(",") if origin.strip()]

    return [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]


@dataclass(slots=True)
class Settings:
    app_name: str = "research-method-platform-api"
    app_version: str = "0.1.0"
    storage_root: Path = field(default_factory=lambda: Path(__file__).resolve().parents[2] / "storage")
    max_csv_size_bytes: int = 10 * 1024 * 1024
    max_xlsx_size_bytes: int = 20 * 1024 * 1024
    allowed_origins: list[str] = field(default_factory=get_allowed_origins)


settings = Settings()
