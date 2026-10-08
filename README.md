# DADA — Directed Ambition Design Agent

An agent skill for ambitious graphic design, packaged from the Graphic Design Agentic Workflow (gdaw). It supports identity, posters, books, editorial design, motion, typography, imagery, data graphics, and interfaces.

The original anchor catalog and graph structure live in a linked reference. DADA traverses that graph non-linearly through a living Frontier, with no move quota, until the critics converge and the stop conditions hold.

## Install

Install with the skills CLI from any project folder:

```sh
npx skills add AnEntrypoint/dada -s dada
```

The CLI detects your agent, copies the `dada` skill into its skills folder, and records it in `skills-lock.json`. Use `npx skills list` to confirm the install.

This repository also includes `.agents/skills/dada`, a relative link to `skills/dada`, for workspace discovery. After opening this project, the skill is available on the next turn.

To copy the skill by hand instead, copy `skills/dada` into your agent’s skills directory, for example `~/.agents/skills/dada`, or `~/.codex/skills/dada` for Codex. Preserve any existing installation before replacing it.

## Use

Invoke `$dada` with a design brief. DADA always pursues maximum artistic ambition and runs in one of two modes, chosen once and stated in the Traversal Plan:

- **Autonomous** judges the work on its own terms (inner necessity and significant form), with no ideology, cause or market as a veto. It is the default unless the brief names a client, audience or public constraint.
- **Adaptive** adds approachability: MAYA, Most Advanced Yet Acceptable, requires both the advanced and the acceptable pole to hold.

The traversal is non-linear: each pass spends one candidate from the Frontier (outgoing, incoming and dotted edges from visited anchors), branches between rival Breakers, and reopens earlier moves when a dependency changes. A move count is never a stopping rule. The run closes only when the five stop conditions hold: no open Frontier items, a WHOLE panel round with every required critic passing, saturation across two consecutive WHOLE rounds, a logged ambition push, and every dotted edge applied or declined. A Lite run (one move, one panel round) happens only on explicit request, and an interrupted run records its Open frontier and resume point in `DESIGN-LOG.md`.

The workflow records a Traversal Plan with its Frontier, Decision Records, Panel Reports, an Anchor Ledger, and a Compliance Check in `DESIGN-LOG.md`. Read `skills/dada/SKILL.md` for the full contract and `skills/dada/references/anchor-graph.md` for the graph. The verdict on every node of that graph from the most recent traversal is in `skills/dada/references/traversal-ledger.md`.

## Validation

Run `python3 scripts/validate_skills.py` with PyYAML installed. GitHub Actions runs the same metadata, reference, and discovery-link validation for pushes and pull requests.
