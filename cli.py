"""graphtour CLI entrypoint.

Batch 0: only `smoke` is wired. ingest/ask arrive in later batches.

  python cli.py smoke      # verify the Cognee backend connection
  python cli.py ingest     # (Batch 1) build the graph from a repo
  python cli.py ask "..."  # (Batch 2) query impact / ownership / provenance
"""

import argparse
import asyncio
import sys


def main() -> None:
    # Windows consoles default to cp1252, which chokes on unicode in LLM output.
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(prog="graphtour")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("smoke", help="verify the Cognee backend connection")
    sub.add_parser("ingest", help="(Batch 1) build the graph from a repo")
    ask = sub.add_parser("ask", help="ask an impact/ownership/provenance question")
    ask.add_argument("question")
    ask.add_argument("--mode", choices=["impact", "ownership", "provenance", "auto"],
                     default="auto", help="which traversal lens to use")
    sub.add_parser("improve", help="enrich/re-weight the repo graph")
    forget = sub.add_parser("forget", help="surgically delete a dataset's memory")
    forget.add_argument("--dataset", required=True)
    sub.add_parser("sync", help="repo changed: forget stale graph, re-ingest, improve")

    args = parser.parse_args()

    if args.command == "smoke":
        from src.smoke_test import main as smoke_main

        asyncio.run(smoke_main())
    elif args.command == "ingest":
        from src.ingest import run_ingest

        asyncio.run(run_ingest())
    elif args.command == "ask":
        from src.recall import run_ask

        asyncio.run(run_ask(args.question, mode=args.mode))
    elif args.command == "improve":
        from src.lifecycle import run_improve

        asyncio.run(run_improve())
    elif args.command == "forget":
        from src.lifecycle import run_forget

        asyncio.run(run_forget(args.dataset))
    elif args.command == "sync":
        from src.lifecycle import run_sync

        asyncio.run(run_sync())


if __name__ == "__main__":
    main()
