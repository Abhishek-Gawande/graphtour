"""Batch 0 smoke test: prove the Cognee backend is reachable end to end.

Run:  python -m src.smoke_test

Remembers one fact, recalls it, and prints the answer. If this passes, the
credentials in .env are good and we can build the real pipeline in Batch 1.
"""

import asyncio

import cognee

from src.config import connect, disconnect


async def main() -> None:
    settings = await connect()
    print(f"[graphtour] connected to '{settings.backend}' backend")

    await cognee.remember(
        "graphtour is a codebase onboarding agent built on Cognee for the "
        "WeMakeDevs x Cognee hackathon.",
        dataset_name="graphtour_smoke",
    )
    print("[graphtour] remember() ok")

    results = await cognee.recall(
        query_text="What is graphtour?",
        datasets=["graphtour_smoke"],  # scope to the dataset we just wrote
    )
    print("[graphtour] recall() ->")
    for r in results:
        text = r.get("text") if isinstance(r, dict) else getattr(r, "text", r)
        print("   ", text)

    await disconnect()


if __name__ == "__main__":
    asyncio.run(main())
