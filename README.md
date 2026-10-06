# DADA — Directed Ambition Design Agent

An agent skill for ambitious graphic design, adapted from the supplied Graphic Design Agentic Workflow (gdaw). It supports identity, posters, books, editorial design, motion, typography, imagery, data graphics, and interfaces.

The original anchor catalog and graph structure live in a linked reference. DADA follows one workflow that expands its traversal and continues for as many moves and critique rounds as the complete brief and strongest achievable artifact require.

## Install

This repository includes `.agents/skills/dada`, a relative link to `skills/dada`, for workspace discovery. After opening this project, the skill is available on the next turn.

For installation across projects, copy `skills/dada` into your agent’s skills directory, for example:

```sh
git clone https://github.com/AnEntrypoint/dada.git
mkdir -p ~/.agents/skills
cp -R dada/skills/dada ~/.agents/skills/dada
```

For Codex, `~/.codex/skills/dada` is also supported. Preserve any existing installation before replacing it.

## Use

Invoke `$dada` with a design brief. DADA always pursues maximum artistic ambition, derives its governing criteria from the brief, and uses as many moves and critique rounds as needed. The workflow includes a Breaker move, independent critics and parallel branches when agent tools are available. Completion requires evidence for the entire brief, resolved objections, and a final inspection with no remaining necessary improvement. There are no selectable effort or aesthetic modes.

The workflow records a Traversal Plan, Decision Records, Panel Reports, an Anchor Ledger, and a Compliance Check in `DESIGN-LOG.md`. Read `skills/dada/SKILL.md` for the full contract and `skills/dada/references/anchor-graph.md` for the graph.

## Validation

Run `python3 scripts/validate_skills.py` with PyYAML installed. GitHub Actions runs the same metadata, reference, and discovery-link validation for pushes and pull requests.
