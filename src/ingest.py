"""Batch 1: ingest a focused slice of a repo into the Cognee graph.

Strategy: don't feed raw code — feed compact *fact documents* that make
relationships explicit, so cognify builds edges we can traverse in Batch 2:

  - per FILE:   path, package, classes/functions defined, internal imports, docstring
    -> defined-in, part-of, imports/depends-on edges
  - per COMMIT: hash, author, date, subject, files touched
    -> modified-by, authored-by edges (ownership + provenance)

Run:  python cli.py ingest
"""

from __future__ import annotations

import ast
import subprocess
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent / "demo" / "target_repo"
REPO_NAME = "cognee"

# The focused slice: Cognee's own memory-lifecycle implementation.
# Demo poetry: graphtour explains how cognee's remember/recall/forget/improve work.
SLICE_PATHS = [
    "cognee/modules/search",
    "cognee/api/v1/search",
    "cognee/api/v1/recall",
    "cognee/api/v1/remember",
    "cognee/api/v1/forget",
    "cognee/api/v1/improve",
    "cognee/api/v1/cognify",
]
MAX_COMMITS = 80


# ── file facts ──────────────────────────────────────────────────────────────

@dataclass
class FileFacts:
    rel_path: str
    package: str
    docstring: str
    classes: list[str]
    functions: list[str]
    internal_imports: list[str]


def _parse_python_file(path: Path, repo_root: Path) -> FileFacts | None:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:
        return None

    rel = path.relative_to(repo_root).as_posix()
    classes, functions, imports = [], [], []

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            classes.append(node.name)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not node.name.startswith("_"):
                functions.append(node.name)
        elif isinstance(node, ast.Import):
            imports.extend(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.append(node.module)

    internal = sorted({m for m in imports if m.split(".")[0] == REPO_NAME})
    return FileFacts(
        rel_path=rel,
        package=rel.rsplit("/", 1)[0].replace("/", "."),
        docstring=(ast.get_docstring(tree) or "").strip().split("\n")[0],
        classes=classes,
        functions=functions[:15],
        internal_imports=internal,
    )


def _file_doc(f: FileFacts) -> str:
    lines = [
        f"The file '{f.rel_path}' is a Python module in the '{f.package}' package "
        f"of the {REPO_NAME} repository."
    ]
    if f.docstring:
        lines.append(f"Its purpose: {f.docstring}")
    if f.classes:
        lines.append(f"It defines the classes: {', '.join(f.classes)}.")
    if f.functions:
        lines.append(f"It defines the functions: {', '.join(f.functions)}.")
    for imp in f.internal_imports:
        lines.append(f"The file '{f.rel_path}' imports and depends on the module '{imp}'.")
    return " ".join(lines)


def collect_file_docs(repo_root: Path = REPO_ROOT) -> list[str]:
    docs = []
    for slice_path in SLICE_PATHS:
        for py in sorted((repo_root / slice_path).rglob("*.py")):
            if py.name == "__init__.py" and py.stat().st_size < 10:
                continue
            facts = _parse_python_file(py, repo_root)
            if facts:
                docs.append(_file_doc(facts))
    return docs


# ── commit facts ────────────────────────────────────────────────────────────

def collect_commit_docs(repo_root: Path = REPO_ROOT, max_commits: int = MAX_COMMITS) -> list[str]:
    out = subprocess.run(
        ["git", "log", f"--max-count={max_commits}", "--name-only",
         "--pretty=format:@@%h|%an|%as|%s", "--", *SLICE_PATHS],
        cwd=repo_root, capture_output=True, text=True, encoding="utf-8", errors="replace",
    ).stdout

    docs = []
    for block in out.split("@@"):
        block = block.strip()
        if not block:
            continue
        header, *files = block.split("\n")
        try:
            sha, author, date, subject = header.split("|", 3)
        except ValueError:
            continue
        touched = [f for f in files if f.strip()][:8]
        doc = (
            f"Commit {sha} in the {REPO_NAME} repository was authored by {author} "
            f"on {date}. Its purpose: \"{subject}\"."
        )
        if touched:
            doc += " It modified the files: " + ", ".join(f"'{t}'" for t in touched) + "."
            doc += f" Therefore {author} has worked on these files and can be asked about them."
        docs.append(doc)
    return docs


# ── main entrypoint ─────────────────────────────────────────────────────────

async def run_ingest(dataset: str | None = None) -> None:
    import cognee

    from src.config import connect, disconnect
    from src.state import active_dataset

    if not REPO_ROOT.exists():
        raise RuntimeError(f"Target repo not found at {REPO_ROOT}. Clone it first.")

    target = dataset or active_dataset()
    file_docs = collect_file_docs()
    commit_docs = collect_commit_docs()
    print(f"[graphtour] extracted {len(file_docs)} file docs, {len(commit_docs)} commit docs")

    settings = await connect()
    print(f"[graphtour] connected to '{settings.backend}' backend — ingesting into '{target}'")

    await cognee.remember(file_docs + commit_docs, dataset_name=target)
    print("[graphtour] remember() accepted — cognify building the graph server-side")

    await disconnect()
    print("[graphtour] ingest complete")
