# Codebase Onboarding Agent — Cognee Hackathon Build

> Context handoff for Claude Code. This file captures everything decided so far so
> work can continue seamlessly. (Auto-loaded by Claude Code as project memory.)

---

## The hackathon

- **Event:** "The Hangover Part AI: Where's My Context?" — WeMakeDevs × Cognee.
- **Dates:** Jun 29 – Jul 5, 2026 (one week).
- **Theme:** Fully open. Build anything — agents, apps, tools, games, automations —
  as long as **Cognee powers the memory**.
- **Cognee = the memory layer for AI agents.** Turns text/files/URLs into a hybrid
  **graph + vector** knowledge store. Self-hosted (open source) or managed (Cloud).

### The three prize avenues (keep them straight)
1. **$100 per PR** — Open Source *PR* track (fixing repo issues). *Separate effort,
   already in progress elsewhere — not this project.*
2. **Best Use of Open Source → MacBook Neo** — best build on **self-hosted** Cognee.
3. **Best Use of Cognee Cloud → iPhone 17** — best build on **Cognee Cloud**.

**This project targets #2 and #3.** The idea is identical for both; only the Cognee
backend differs (config switch). Build backend-agnostic. **OPEN QUESTION to confirm in
Discord:** can one submission be entered in both award categories, or is it one track
per submission? If one-per-submission, we pick at the end; architecture stays the same.

### Memory lifecycle API (lean on ALL FOUR — this is scored twice)
```python
import cognee
await cognee.remember("...")           # ingest text/files/URLs into the graph
answer = await cognee.recall("...")    # auto-routes: semantic similarity + graph traversal
await cognee.improve()                 # a.k.a. memify — enrich, prune stale, reweight on feedback
await cognee.forget(dataset="...")     # surgically delete when no longer needed
```

### Judging criteria (6)
1. **Potential Impact** — real, meaningful problem.
2. **Creativity & Innovation** — pushes what "never forgets" can do.
3. **Technical Excellence** — clean, maintainable engineering.
4. **Best Use of Cognee** — how DEEPLY it uses the lifecycle APIs + hybrid graph-vector.
5. **User Experience** — polished, adoptable.
6. **Presentation Quality** — demo, README, submission clarity.

### Submission deliverables (confirm exact list on Cognee's submission template)
- Public **GitHub repo with visible commit history** (first commit ON/AFTER Jun 29).
- **README** explaining problem / solution / impact.
- **~2-min demo video** (mandatory in prior WeMakeDevs events — verify).
- **Disclose AI-assistant use** (Claude Code) in the submission — required, non-negotiable.

### Rules that affect us now
- Pre-event **planning/notes/sketches/diagrams are allowed** (this file is fine).
- **Coding/design must start only after Jun 29.** No project code or repo commits yet.
- Free Cognee Cloud Developer plan ($35) with code `COGNEE-35` at platform.cognee.ai.

---

## THE STRATEGIC INSIGHT (why we'll win, or not)

The judges *built* the memory layer. A generic "chat with your PDF" RAG app dies.
Two of six criteria reward **depth of Cognee use**. So:

1. **Use the GRAPH, not just vectors.** The killer feature must only work because of
   *relationships between facts* + traversal — not similarity search alone.
2. **Make `improve()` and `forget()` load-bearing.** Everyone does remember+recall.
   Almost nobody uses the other two for real. We do.

---

## THE CHOSEN IDEA: Codebase Onboarding Agent

**One-liner:** An agent that ingests a repo (code + commits + PRs + docs) into a
Cognee graph, so a new contributor can ask *"why does this module exist, who owns it,
what breaks if I change X?"* and get answers by **traversing** the
dependency + ownership + history graph — not by grepping.

**Why it wins:**
- **Code is literally a graph** → maximally on-theme for "Best Use of Cognee."
- **Graph-native queries** (impact analysis, ownership, provenance) that plain RAG can't do.
- Uses all four ops naturally: `remember` (ingest repo), `recall` (traverse), `improve`
  (re-weight as the repo evolves / on feedback), `forget` (prune deleted code & dead paths).
- **Killer presentation move: DEMO IT ON `topoteretes/cognee` ITSELF.** Showing the Cognee
  team a tool that understands *their own* codebase is a memory they won't forget.
  (We already know that repo well from PR-track work — home turf.)

**Graph shape (draft):**
- Nodes: files, modules, functions/classes, PRs, commits, authors, docs, issues.
- Edges: imports/depends-on, defined-in, modified-by, owned-by, references,
  superseded-by, documented-in.
- Recall traverses these for: impact ("what breaks if I touch X"), ownership
  ("who to ask"), provenance ("why does this exist / which PR/issue introduced it").

**Backend switch for dual-track:**
- Self-hosted config → eligible for MacBook track.
- Cloud config (`COGNEE-35`) → eligible for iPhone track.
- Keep one code path; select backend via env/config.

---

## Other ideas considered (for reference / fallback)
1. **"Why did we decide that?"** — decision memory for teams (decisions→rationale→people→
   superseded-by). Strong graph story, broad appeal. *Best runner-up.*
2. **Codebase onboarding agent** — CHOSEN.
3. **Contradiction-catching research copilot** — flags when newer sources contradict older
   graph beliefs; memify reweights, forget prunes retracted sources.
4. **NPC that remembers (memory game)** — NPCs remember across sessions, gossip via social
   graph (memify), forget minor events. Creative wildcard, memorable demo, on-theme.
5. **Personal relationship manager** — people/relationship graph; safe but crowded space.

---

## NEXT STEPS (in Claude Code, from Jun 29)
1. Confirm dual-track eligibility in Discord.
2. Sign up Cognee Cloud (`COGNEE-35`); get self-hosted Cognee running locally.
3. Create the public GitHub repo; first commit in-window.
4. Nail the smallest graph slice that answers ONE impressive traversal query end-to-end,
   then expand. Wire all four lifecycle ops early so "Best Use of Cognee" is real, not bolted on.
5. Script the demo around the "understands Cognee's own repo" moment.

## Resources to collect in this folder (TODO)
- [ ] Cognee quickstart + lifecycle API reference (self-hosted AND Cloud).
- [ ] Cognee config docs (graph store, vector store, LLM provider).
- [ ] Notes on `topoteretes/cognee` repo structure (the dogfood target).
- [ ] One-week day-by-day build plan.
- [ ] Demo video script + README skeleton.
