"""Batch 3: the load-bearing lifecycle ops most submissions skip.

  improve() — enrich/re-weight the graph after new knowledge arrives
              (post-ingest, or after agents store insights via MCP).
  forget()  — keep the memory truthful: when the repo changes, the stale
              graph version is dropped and the slice re-learned.

Sync uses VERSIONED datasets (graphtour_repo -> _v2 -> _v3): Cognee Cloud
leaves a forgotten dataset's name in a broken state (re-remembering into it
409s), so we never reuse names. Remember fresh version, switch the active
pointer, then forget the old one.

Run:  python cli.py improve
      python cli.py forget --dataset <name>
      python cli.py sync
"""

from __future__ import annotations

from src.state import active_dataset, next_version, set_active_dataset


async def improve_graph(dataset: str | None = None) -> str:
    """Enrich/re-weight the dataset's graph. Assumes caller connected.

    Cognee Cloud does not expose /api/v1/improve yet (verified via the tenant's
    OpenAPI spec), so on cloud we fall back to cognify re-enrichment — the same
    graph-building pass improve() wraps. Self-hosted uses improve() natively.
    """
    import cognee

    target = dataset or active_dataset()
    try:
        await cognee.improve(target)
        return "improve() complete — graph enriched/re-weighted"
    except RuntimeError as err:
        if "404" not in str(err):
            raise
        await cognee.cognify(datasets=[target])
        return (
            "improve() not exposed by Cognee Cloud yet — fell back to cognify "
            "re-enrichment on the dataset (same graph-building pass improve wraps)"
        )


async def run_improve(dataset: str | None = None) -> None:
    from src.config import connect, disconnect

    target = dataset or active_dataset()
    await connect()
    print(f"[graphtour] improve() running on '{target}' — enriching the graph...")
    print(f"[graphtour] {await improve_graph(target)}")
    await disconnect()


async def run_forget(dataset: str) -> None:
    """Surgically delete a dataset's memory (e.g. a repo that was removed)."""
    import cognee

    from src.config import connect, disconnect

    await connect()
    print(f"[graphtour] forget() deleting dataset '{dataset}'...")
    result = await cognee.forget(dataset=dataset)
    print(f"[graphtour] forget() result: {result}")
    await disconnect()


async def run_sync() -> None:
    """Repo evolved? Re-learn the current slice, then forget the stale graph.

    remember(new version) -> improve() -> switch active pointer -> forget(old):
    the full memory lifecycle in one command. Deleted files vanish from the
    graph because they no longer exist in the re-ingested slice.
    """
    import cognee

    from src.config import connect, disconnect
    from src.ingest import collect_commit_docs, collect_file_docs

    old = active_dataset()
    new = next_version()

    file_docs = collect_file_docs()
    commit_docs = collect_commit_docs()
    print(f"[graphtour] sync: fresh slice = {len(file_docs)} files, {len(commit_docs)} commits")

    await connect()
    print(f"[graphtour] sync: remember() fresh slice into '{new}'...")
    await cognee.remember(file_docs + commit_docs, dataset_name=new)
    print(f"[graphtour] sync: {await improve_graph(new)}")

    set_active_dataset(new)
    print(f"[graphtour] sync: active dataset switched '{old}' -> '{new}'")

    print(f"[graphtour] sync: forget() stale '{old}'...")
    result = await cognee.forget(dataset=old)
    print(f"[graphtour] sync: forget() result: {result}")
    print("[graphtour] sync complete — memory matches the repo again")
    await disconnect()
