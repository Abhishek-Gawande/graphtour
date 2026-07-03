"""graphtour MCP server — persistent codebase memory for coding agents.

Exposes the graph queries as MCP tools so Claude Code (or any MCP client) can
ask a Cognee-backed knowledge graph about the codebase it is working on:

    ask_impact      what breaks if I change X?          (import/depends-on edges)
    ask_ownership   who should I ask about X?           (author->commit->file edges)
    ask_provenance  why does X exist?                   (commit-history edges)
    remember_insight  store a new fact the agent learned (feeds improve())

Register with Claude Code via .mcp.json (checked in) or:
    claude mcp add graphtour -- python mcp_server.py
"""

import contextlib
import sys

from mcp.server.fastmcp import FastMCP

from src.recall import ask
from src.ingest import DATASET

mcp = FastMCP("graphtour")

_connected = False

# stdio transport: stdout carries the MCP protocol. Cognee prints status lines
# to stdout, which would corrupt JSON-RPC framing — shove them to stderr.
_shield = lambda: contextlib.redirect_stdout(sys.stderr)  # noqa: E731


async def _ensure_connected() -> None:
    """Connect to the Cognee backend once, on first tool call."""
    global _connected
    if not _connected:
        from src.config import connect

        print("[graphtour-mcp] connecting to Cognee...", file=sys.stderr, flush=True)
        with _shield():
            await connect()
        print("[graphtour-mcp] connected", file=sys.stderr, flush=True)
        _connected = True


@mcp.tool()
async def ask_impact(question: str) -> str:
    """Impact analysis: what breaks if a file/module/function changes?
    Traverses import/depends-on edges in the codebase knowledge graph.
    Example: 'what breaks if I change cognee/modules/search/methods/search.py?'"""
    await _ensure_connected()
    with _shield():
        return await ask(question, mode="impact")


@mcp.tool()
async def ask_ownership(question: str) -> str:
    """Ownership: who wrote / maintains this code and who is best to ask?
    Aggregates author->commit->file edges from real git history.
    Example: 'who has worked on the search module?'"""
    await _ensure_connected()
    with _shield():
        return await ask(question, mode="ownership")


@mcp.tool()
async def ask_provenance(question: str) -> str:
    """Provenance: why does this code exist and how did it evolve?
    Reconstructs history from commit edges, citing hashes, authors, dates.
    Example: 'why does the improve API exist?'"""
    await _ensure_connected()
    with _shield():
        return await ask(question, mode="provenance")


@mcp.tool()
async def ask_codebase(question: str) -> str:
    """General question about the codebase, answered from the knowledge graph
    (auto-routed between semantic similarity and graph traversal)."""
    await _ensure_connected()
    with _shield():
        return await ask(question, mode="auto")


@mcp.tool()
async def remember_insight(insight: str) -> str:
    """Store a durable insight about the codebase (a gotcha, a decision, a
    convention) so future agent sessions recall it. This is how the memory
    outlives your context window."""
    import cognee

    await _ensure_connected()
    with _shield():
        await cognee.remember(insight, dataset_name=DATASET)
    return f"Remembered into '{DATASET}'. Future sessions will recall this."


if __name__ == "__main__":
    mcp.run()  # stdio transport — what Claude Code speaks
