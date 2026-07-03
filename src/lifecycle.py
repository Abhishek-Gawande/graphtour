"""Batch 3: the load-bearing lifecycle ops most submissions skip.

  improve() — enrich/re-weight the graph after new knowledge arrives
              (post-ingest, or after agents store insights via MCP).
  forget()  — keep the memory truthful: when the repo changes, stale
              knowledge is surgically dropped and the slice re-learned.

Run:  python cli.py improve
      python cli.py forget --dataset graphtour_smoke
      python cli.py sync           # forget stale graph -> re-ingest fresh slice
"""

from __future__ import annotations

from src.ingest import DATASET


async def run_improve(dataset: str = DATASET) -> None:
    """Ask Cognee to enrich and re-weight the dataset's graph."""
    import cognee

    from src.config import connect, disconnect

    await connect()
    print(f"[graphtour] improve() running on '{dataset}' — enriching the graph...")
    await cognee.improve(dataset)
    print("[graphtour] improve() complete — graph enriched/re-weighted")
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
    """Repo evolved? Drop the stale graph and re-learn the current slice.

    forget(stale) -> remember(fresh) -> improve(): the full memory lifecycle
    in one command. Deleted files vanish from the graph because they no longer
    exist in the re-ingested slice.
    """
    import cognee

    from src.config import connect, disconnect
    from src.ingest import collect_commit_docs, collect_file_docs

    file_docs = collect_file_docs()
    commit_docs = collect_commit_docs()
    print(f"[graphtour] sync: fresh slice = {len(file_docs)} files, {len(commit_docs)} commits")

    await connect()
    print(f"[graphtour] sync: forget() stale '{DATASET}'...")
    await cognee.forget(dataset=DATASET)
    print("[graphtour] sync: remember() fresh slice...")
    await cognee.remember(file_docs + commit_docs, dataset_name=DATASET)
    print("[graphtour] sync: improve() to enrich the rebuilt graph...")
    await cognee.improve(DATASET)
    print("[graphtour] sync complete — memory matches the repo again")
    await disconnect()
