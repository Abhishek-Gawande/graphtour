"""Tracks which dataset version is live.

Cognee Cloud has a quirk: a forgotten dataset's NAME stays in a broken state
server-side, so re-remembering into it 409s. The fix is to never reuse names:
sync writes graphtour_repo_v2, v3, ... and forgets the old version. This file
remembers which version is active; everything that reads the graph asks here.
"""

from __future__ import annotations

import json
from pathlib import Path

DEFAULT_DATASET = "graphtour_repo"
_STATE_PATH = Path(__file__).resolve().parent.parent / ".graphtour_state.json"


def active_dataset() -> str:
    if _STATE_PATH.exists():
        return json.loads(_STATE_PATH.read_text(encoding="utf-8"))["active_dataset"]
    return DEFAULT_DATASET


def set_active_dataset(name: str) -> None:
    _STATE_PATH.write_text(
        json.dumps({"active_dataset": name}, indent=1), encoding="utf-8"
    )


def next_version() -> str:
    current = active_dataset()
    if "_v" in current and current.rsplit("_v", 1)[1].isdigit():
        base, n = current.rsplit("_v", 1)
        return f"{base}_v{int(n) + 1}"
    return f"{current}_v2"
