"""Thin REST client for Cognee Cloud.

The Python SDK's serve() hangs when running inside an MCP stdio subprocess
(verified: works in CLI and plain anyio, hangs under FastMCP even with a
thread-isolated loop). The tenant's REST API works everywhere, so the MCP
server talks to it directly. Field names come from the tenant's OpenAPI spec
(RecallPayloadDTO is camelCase; RememberEntryRequest is snake_case).
"""

from __future__ import annotations

import os

import requests

from src.ingest import DATASET


def _conn() -> tuple[str, dict]:
    from dotenv import load_dotenv

    load_dotenv()
    base = os.environ.get("COGNEE_CLOUD_URL")
    key = os.environ.get("COGNEE_API_KEY")
    if not base or not key:
        raise RuntimeError("COGNEE_CLOUD_URL / COGNEE_API_KEY not set (see .env.example)")
    return base.rstrip("/"), {"X-Api-Key": key}


def recall(query: str, system_prompt: str, dataset: str = DATASET, top_k: int = 20) -> str:
    base, headers = _conn()
    resp = requests.post(
        f"{base}/api/v1/recall",
        headers=headers,
        json={
            "query": query,
            "datasets": [dataset],
            "topK": top_k,
            "systemPrompt": system_prompt,
        },
        timeout=180,
    )
    resp.raise_for_status()
    data = resp.json()
    items = data if isinstance(data, list) else [data]
    texts = []
    for item in items:
        text = item.get("text") if isinstance(item, dict) else None
        if text:
            texts.append(str(text))
    return "\n".join(texts) if texts else "(no answer from the graph)"


def remember_entry(entry: str, dataset: str = DATASET) -> None:
    base, headers = _conn()
    resp = requests.post(
        f"{base}/api/v1/remember/entry",
        headers=headers,
        json={"entry": entry, "dataset_name": dataset},
        timeout=120,
    )
    resp.raise_for_status()
