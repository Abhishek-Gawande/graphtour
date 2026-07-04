"""graphtour MCP server — persistent codebase memory for coding agents.

Exposes the graph queries as MCP tools so Claude Code (or any MCP client) can
ask a Cognee-backed knowledge graph about the codebase it is working on:

    ask_impact        what breaks if I change X?          (import/depends-on edges)
    ask_ownership     who should I ask about X?           (author->commit->file edges)
    ask_provenance    why does X exist?                   (commit-history edges)
    ask_codebase      anything else, auto-routed
    remember_insight  store a durable fact that outlives the agent's context window

Talks to Cognee Cloud over REST (src/cloud_rest.py) — the Python SDK's serve()
hangs inside MCP stdio subprocesses, the REST API does not.

Register with Claude Code via .mcp.json (checked in) or:
    claude mcp add graphtour -- python mcp_server.py
"""

import asyncio

from mcp.server.fastmcp import FastMCP

from src import cloud_rest
from src.recall import MENTOR_PROMPT, MODES
from src.state import active_dataset

mcp = FastMCP("graphtour")


async def _graph_ask(question: str, mode: str) -> str:
    query = MODES[mode].format(q=question)
    # requests is blocking; keep the MCP loop responsive
    return await asyncio.to_thread(cloud_rest.recall, query, MENTOR_PROMPT)


@mcp.tool()
async def ask_impact(question: str) -> str:
    """Impact analysis: what breaks if a file/module/function changes?
    Traverses import/depends-on edges in the codebase knowledge graph.
    Example: 'what breaks if I change cognee/modules/search/methods/search.py?'"""
    return await _graph_ask(question, mode="impact")


@mcp.tool()
async def ask_ownership(question: str) -> str:
    """Ownership: who wrote / maintains this code and who is best to ask?
    Aggregates author->commit->file edges from real git history.
    Example: 'who has worked on the search module?'"""
    return await _graph_ask(question, mode="ownership")


@mcp.tool()
async def ask_provenance(question: str) -> str:
    """Provenance: why does this code exist and how did it evolve?
    Reconstructs history from commit edges, citing hashes, authors, dates.
    Example: 'why does the improve API exist?'"""
    return await _graph_ask(question, mode="provenance")


@mcp.tool()
async def ask_codebase(question: str) -> str:
    """General question about the codebase, answered from the knowledge graph
    (auto-routed between semantic similarity and graph traversal)."""
    return await _graph_ask(question, mode="auto")


@mcp.tool()
async def remember_insight(insight: str) -> str:
    """Store a durable insight about the codebase (a gotcha, a decision, a
    convention) so future agent sessions recall it. This is how the memory
    outlives your context window."""
    await asyncio.to_thread(cloud_rest.remember_text, insight)
    return f"Remembered into '{active_dataset()}'. Future sessions will recall this."


if __name__ == "__main__":
    mcp.run()  # stdio transport — what Claude Code speaks
