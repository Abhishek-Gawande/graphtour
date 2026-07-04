"""Backend configuration for graphtour.

One code path, two backends. `COGNEE_BACKEND` in .env selects which:
  - "cloud" -> Cognee Cloud (iPhone track). Connects with cognee.serve(url, api_key).
  - "local" -> self-hosted Cognee (MacBook track). No serve() call; uses local stores.

Keeping the switch here means ingest/recall/lifecycle never care which backend
is active — they just `await connect()` first.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    backend: str
    cloud_url: str | None
    api_key: str | None
    tenant_id: str | None
    user_id: str | None
    llm_api_key: str | None


def load_settings() -> Settings:
    return Settings(
        backend=os.getenv("COGNEE_BACKEND", "cloud").strip().lower(),
        cloud_url=os.getenv("COGNEE_CLOUD_URL") or None,
        api_key=os.getenv("COGNEE_API_KEY") or None,
        tenant_id=os.getenv("COGNEE_TENANT_ID") or None,
        user_id=os.getenv("COGNEE_USER_ID") or None,
        llm_api_key=os.getenv("LLM_API_KEY") or None,
    )


async def connect() -> Settings:
    """Connect to the selected Cognee backend. Idempotent enough for CLI use.

    Returns the resolved Settings so callers can log which backend is live.
    """
    import cognee  # imported lazily so `--help` etc. work without the SDK installed

    settings = load_settings()

    if settings.backend == "cloud":
        if not settings.cloud_url or not settings.api_key:
            raise RuntimeError(
                "Cloud backend selected but COGNEE_CLOUD_URL / COGNEE_API_KEY are unset. "
                "Fill them in .env (see .env.example)."
            )
        await cognee.serve(url=settings.cloud_url, api_key=settings.api_key)
    elif settings.backend == "local":
        # Self-hosted: no serve(); embedded stores + local cognify runs.
        if not settings.llm_api_key:
            raise RuntimeError(
                "Local backend selected but LLM_API_KEY is unset. "
                "Fill it in .env (see .env.example)."
            )
        # cognee reads the LLM key from the environment (dotenv already loaded it,
        # this keeps it explicit and works even if .env discovery ever fails).
        os.environ.setdefault("LLM_API_KEY", settings.llm_api_key)
        # Keep all local stores inside the project, NOT the SDK's install dir
        # (Windows Store Python site-packages is effectively read-only).
        local_root = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cognee_data")
        cognee.config.system_root_directory(os.path.join(local_root, "system"))
        cognee.config.data_root_directory(os.path.join(local_root, "data"))
    else:
        raise RuntimeError(
            f"Unknown COGNEE_BACKEND={settings.backend!r}. Use 'cloud' or 'local'."
        )

    return settings


async def disconnect() -> None:
    import cognee

    settings = load_settings()
    if settings.backend == "cloud":
        await cognee.disconnect()
