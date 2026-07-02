# graphtour

> *Never ask "who knows this code?" again.* graphtour turns any repo into a queryable graph memory , powered by [Cognee](https://www.cognee.ai).

Ask your codebase **"what breaks if I change this?"** graphtour ingests a repo's
code, commits, and PRs into a Cognee knowledge graph and answers by *traversing*
dependencies, ownership, and history instead of grepping.

Built for the **WeMakeDevs × Cognee** hackathon 

---

## The problem

A new contributor drops into an unfamiliar repo and asks the questions grep can't answer:
- *"What breaks if I change this function?"* (impact)
- *"Who should I ask about this module?"* (ownership)
- *"Why does this even exist , which PR introduced it?"* (provenance)

These are **relationship** questions. Keyword search and plain RAG can't follow the
edges between files, commits, authors, and PRs. A graph can.

## The solution

graphtour models a codebase as what it actually is , a graph and uses Cognee's
memory lifecycle to keep that graph honest as the repo evolves:

| Cognee verb | graphtour uses it to |
|-------------|----------------------|
| `remember`  | ingest files, commits, PRs, authors and their edges into the graph |
| `recall`    | traverse the graph to answer impact / ownership / provenance questions |
| `improve`   | re-weight and enrich the graph as the repo changes and on feedback |
| `forget`    | prune deleted files and dead paths so the memory stays truthful |

**Demo:** graphtour onboards you to *Cognee's own* repository.

## Backends

One code path, two backends , selected by `COGNEE_BACKEND` in `.env`:
- **cloud**  [Cognee Cloud](https://platform.cognee.ai)
- **local**  self-hosted, open-source Cognee

## Quickstart

```bash
python -m venv .venv && . .venv/Scripts/activate   # Windows
pip install -r requirements.txt
cp .env.example .env        # then fill in your Cognee Cloud URL + API key
python cli.py smoke         # verify the connection
```

## Status

- [x] Batch 0  scaffold, config switch, connection smoke test
- [ ] Batch 1  ingest a repo into the graph
- [ ] Batch 2  impact / ownership / provenance queries
- [ ] Batch 3  `improve()` + `forget()` on repo changes
- [ ] Batch 4  UX + demo
- [ ] Batch 5  README polish, demo video, submission

---

*Built with the assistance of Claude Code (Anthropic).*
