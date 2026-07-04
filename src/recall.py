"""Batch 2: the killer traversal queries.

Three questions plain RAG can't answer well, because each needs edges, not
similarity: impact (imports/depends-on), ownership (authored/modified-by),
provenance (commit -> purpose -> file). All run against the graph built by
src/ingest.py in the `graphtour_repo` dataset.

Run:  python cli.py ask "what breaks if I change search.py?" --mode impact
"""

from __future__ import annotations

from src.state import active_dataset

MENTOR_PROMPT = (
    "You are graphtour, a codebase onboarding mentor. Answer from the knowledge "
    "graph context only — never invent files, people, or commits. Cite file paths, "
    "author names, and commit hashes from the context. Be concise and concrete. "
    "If the graph lacks the answer, say exactly what is missing."
)

# Mode -> how we phrase the traversal ask. The phrasing steers graph completion
# toward the edge types that matter for that question.
MODES = {
    "impact": (
        "Impact analysis: {q} — Which files import or depend on the code in "
        "question, directly or transitively? List every dependent file path and "
        "explain what would break and why."
    ),
    "ownership": (
        "Ownership: {q} — Which people have authored commits that modified the "
        "relevant files? Name each person, how recently and how often they touched "
        "these files, and who is the best person to ask."
    ),
    "provenance": (
        "Provenance: {q} — Why does this code exist? Which commits created or "
        "changed it, by whom, when, and for what stated purpose? Give a short "
        "history, citing commit hashes."
    ),
    "auto": "{q}",
}


async def ask(question: str, mode: str = "auto", top_k: int = 20) -> str:
    """One graph-traversal answer. Assumes the caller has already connected."""
    import cognee

    if mode not in MODES:
        raise ValueError(f"Unknown mode '{mode}'. Use one of: {', '.join(MODES)}")

    results = await cognee.recall(
        query_text=MODES[mode].format(q=question),
        datasets=[active_dataset()],
        top_k=top_k,
        system_prompt=MENTOR_PROMPT,
    )

    answers = []
    for r in results:
        text = r.get("text") if isinstance(r, dict) else getattr(r, "text", None)
        if text:
            answers.append(str(text))
    return "\n".join(answers) if answers else "(no answer from the graph)"


async def run_ask(question: str, mode: str = "auto") -> None:
    from src.config import connect, disconnect

    settings = await connect()
    print(f"[graphtour] {mode} query against '{active_dataset()}' ({settings.backend})\n")
    print(await ask(question, mode=mode))
    await disconnect()
