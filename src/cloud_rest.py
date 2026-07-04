"""Thin REST client for Cognee Cloud.

The Python SDK's serve() hangs when running inside an MCP stdio subprocess
(verified: works in CLI and plain anyio, hangs under FastMCP even with a
thread-isolated loop). The tenant's REST API works everywhere, so the MCP
server talks to it directly. Field names come from the tenant's OpenAPI spec
(RecallPayloadDTO is camelCase; /remember is multipart like the SDK sends).
"""

from __future__ import annotations

import os

import requests

from src.state import active_dataset


def _conn() -> tuple[str, dict]:
    from dotenv import load_dotenv

    load_dotenv()
    base = os.environ.get("COGNEE_CLOUD_URL")
    key = os.environ.get("COGNEE_API_KEY")
    if not base or not key:
        raise RuntimeError("COGNEE_CLOUD_URL / COGNEE_API_KEY not set (see .env.example)")
    return base.rstrip("/"), {"X-Api-Key": key}


def recall(query: str, system_prompt: str, dataset: str | None = None, top_k: int = 20) -> str:
    base, headers = _conn()
    resp = requests.post(
        f"{base}/api/v1/recall",
        headers=headers,
        json={
            "query": query,
            "datasets": [dataset or active_dataset()],
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


def remember_text(text: str, dataset: str | None = None) -> None:
    """Store one text document, same multipart shape the SDK's remember() sends."""
    base, headers = _conn()
    resp = requests.post(
        f"{base}/api/v1/remember",
        headers=headers,
        files=[("data", ("data.txt", text.encode("utf-8"), "text/plain"))],
        data={"datasetName": dataset or active_dataset()},
        timeout=300,
    )
    resp.raise_for_status()
