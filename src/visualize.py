"""Render the codebase knowledge graph as an interactive HTML page.

Pulls nodes/edges straight from the Cognee Cloud graph endpoint and writes a
self-contained force-directed viz (vis-network via CDN). Demo money-shot:
SEE the graph that answers the questions.

Run:  python cli.py graph          # writes demo/graph.html and prints the path
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import requests

from src.state import active_dataset

OUT_PATH = Path(__file__).resolve().parent.parent / "demo" / "graph.html"

# node type -> color (vis-network). Code entities pop, plumbing fades.
PALETTE = {
    "TextSummary": "#c8c8c8",
    "DocumentChunk": "#e0e0e0",
    "TextDocument": "#b0bec5",
    "Entity": "#4fc3f7",
    "EntityType": "#9575cd",
}
DEFAULT_COLOR = "#ffb74d"

HTML = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>graphtour — codebase knowledge graph</title>
<script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
<style>
  body {{ margin:0; font-family: system-ui, sans-serif; background:#111; color:#eee; }}
  #bar {{ padding:10px 16px; background:#1a1a2e; }}
  #bar b {{ color:#4fc3f7; }}
  #net {{ width:100vw; height: calc(100vh - 46px); }}
</style></head><body>
<div id="bar"><b>graphtour</b> — knowledge graph of the '{dataset}' slice
  &nbsp;·&nbsp; {n_nodes} nodes, {n_edges} edges &nbsp;·&nbsp; powered by Cognee</div>
<div id="net"></div>
<script>
  const nodes = new vis.DataSet({nodes_json});
  const edges = new vis.DataSet({edges_json});
  new vis.Network(document.getElementById("net"), {{nodes, edges}}, {{
    physics: {{ solver: "forceAtlas2Based", stabilization: {{ iterations: 120 }} }},
    nodes: {{ shape: "dot", size: 8, font: {{ color: "#ddd", size: 11 }} }},
    edges: {{ color: {{ color: "#555" }}, arrows: "to", font: {{ color:"#888", size: 8 }} }},
    interaction: {{ hover: true, tooltipDelay: 100 }},
  }});
</script></body></html>
"""


def fetch_graph() -> tuple[list[dict], list[dict]]:
    from dotenv import load_dotenv

    load_dotenv()
    base = os.environ["COGNEE_CLOUD_URL"]
    headers = {"X-Api-Key": os.environ["COGNEE_API_KEY"]}

    datasets = requests.get(f"{base}/api/v1/datasets/", headers=headers, timeout=30).json()
    repo = next(d for d in datasets if d["name"] == active_dataset())
    data = requests.get(
        f"{base}/api/v1/datasets/{repo['id']}/graph", headers=headers, timeout=120
    ).json()
    return data["nodes"], data["edges"]


def render(nodes: list[dict], edges: list[dict], out_path: Path = OUT_PATH) -> Path:
    vis_nodes = []
    for n in nodes:
        ntype = n.get("type", "?")
        name = (n.get("properties") or {}).get("name") or n.get("label", "")[:40]
        vis_nodes.append({
            "id": n["id"],
            "label": str(name)[:32],
            "title": f"{ntype}: {name}",
            "color": PALETTE.get(ntype, DEFAULT_COLOR),
        })
    vis_edges = [
        {"from": e["source"], "to": e["target"], "label": e.get("label", "")}
        for e in edges
    ]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        HTML.format(
            dataset=active_dataset(),
            n_nodes=len(vis_nodes),
            n_edges=len(vis_edges),
            nodes_json=json.dumps(vis_nodes),
            edges_json=json.dumps(vis_edges),
        ),
        encoding="utf-8",
    )
    return out_path


def run_graph() -> None:
    nodes, edges = fetch_graph()
    path = render(nodes, edges)
    print(f"[graphtour] graph rendered: {len(nodes)} nodes, {len(edges)} edges")
    print(f"[graphtour] open in browser: {path}")
