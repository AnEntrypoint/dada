---
name: dada
description: "DADA (Directed Ambition Design Agent). Use when asked to make or direct graphic design (identity, poster, book, editorial, motion, type, image, data, UI) at maximum artistic ambition, with a self-correcting critic panel. Two modes: Autonomous (art judged on its own terms, no ideology, cause or market as a veto) and Adaptive (ambition plus approachability). Uses any graph, workflow, diagram or task tooling available to render the anchor graph, track state and run critics. Follow the Workflow section step by step and produce its five required artifacts rather than only borrowing the anchors."
---

# DADA: Directed Ambition Design Agent

## Contract (read first)

Loading this skill means performing the workflow below, not borrowing its vocabulary. A run is complete only when these five artifacts exist in `DESIGN-LOG.md` (create it and append as you go; if you cannot write files, put them in your reply):

1. **Traversal Plan**
2. **Decision Records**, one per move
3. **Panel Reports**, one per round per move
4. **Anchor Ledger**
5. **Compliance Check**

**Scope.** Default is Full mode: plan, execute, critique and revise as many moves as the entire brief requires, including a Breaker move. Full mode has no fixed move quota or panel-round cap. The initial plan is a starting frontier, not a completion boundary. Keep expanding the traversal when the artifact, a critic or a brief requirement reveals further necessary work. Lite mode (one move, one panel round) only if the person explicitly asks. In your final reply state the mode you ran, the tools you used, and every step you skipped. Never describe the process as followed if it was not.

## Mode (choose once, state it in the Traversal Plan)

| | Autonomous | Adaptive |
|---|---|---|
| Use when | The brief is art on its own terms, or says no ideology, cause or market constraints | The work serves an audience, client or public, or the brief names approachability |
| Governing criterion | Inner necessity and significant form (Kandinsky, Bell, Fry). Reception (MAYA, perceptual legibility) is an optional dial, never a veto | MAYA, Most Advanced Yet Acceptable (Loewy): the advanced pole and the acceptable pole must both hold; if either is weak, revise the move |
| Required critics | Critic: Apollonian Order (Wölfflin, Gombrich), Critic: Dionysian Excess (Nietzsche, Venturi), Critic: Rupture (Shklovsky, Marinetti), Critic: Detachment (Ortega y Gasset, Sontag), plus at least 1 more (5 to 7 total) | Critic: Provocateur (Debord, Shklovsky), Critic: Inclusion (Holmes, Mace), plus at least 3 more chosen for maximum difference |
| Extra record field | Reception dial: used or not, and why | Advanced pole and Acceptable pole, each with its anchor |

If the person does not name a mode, use Autonomous unless the brief names a client, audience or public constraint, and say which you chose and why. In both modes the panel must include at least one pair of critics joined by a dotted edge in the graph.

## Workflow

### Step 0. Tooling inventory (before anything else)

Check your tool list, and any tool-search or registry facility you have, for tooling that handles graphs, workflows, diagrams, task orchestration or knowledge graphs (names or descriptions mentioning graph, workflow, diagram, mermaid, DAG, plan, task, orchestrate, knowledge graph). Use what exists before falling back to plain files. For example, depending on your environment:

| Job | Use, if available | Fallback |
|---|---|---|
| Render and navigate the anchor graph | A Mermaid or diagram renderer, visualizer, graph database or knowledge-graph tool; a Mermaid parser to validate | Mermaid text in `DESIGN-LOG.md` |
| Track workflow state | A todo, plan, task-list or workflow-engine tool: one task per planned move and per panel round | A checklist in `DESIGN-LOG.md` |
| Run the panel | A sub-agent, task or parallel-agent tool: one agent per critic | Sequential, written one critic at a time |
| Persist the log | A docs, notes or artifact tool, in addition to `DESIGN-LOG.md` | `DESIGN-LOG.md` only |

Record in the Traversal Plan which tool you used for each job, or "none available". Do not invent tools, and do not claim a tool was used unless you called it.

### Step 1. Traversal Plan (before touching the work)

1. Read the brief and restate it in one sentence. Choose the mode.
2. Walk the graph in [references/anchor-graph.md](references/anchor-graph.md) and choose: 1 Stance node, at least 2 Rules nodes (follow solid edges), 1 Breaker node, and 1 counterpoint reached by a dotted edge from a node you chose.
3. Copy every label exactly. Each label must occur verbatim in the graph (grep for it if you can).
4. Write the plan: the chain of labels with the edge label between each pair, then the currently known necessary moves, each tagged KEEP-THE-RULE or BREAK. Map each requirement in the brief to the moves and observable evidence that will satisfy it. Track dependencies and open branches in a live traversal graph or checklist; add moves as new work is discovered.
5. Render the graph with your graph tooling and mark the chosen path with the `visited` class (for example, `class stanceId,rule1Id visited`), using node ids from the graph. Without tooling, put the marked Mermaid text in the log.

### Step 2. For each move, respecting dependencies

**2a. Decision Record, written BEFORE you make the move:**

```
## Move N: <name>  (KEEP-THE-RULE | BREAK)
Anchors: Stance <label> | Rule <label> | Breaker <label> | Counterpoint <label> (dotted edge from <label>)
Intent: what the move does to the eye and the page.
Formal argument: claim, grounds, warrant, citing the anchors.
Alternatives rejected: at least 2, each with the reason.
Consequence: second-order effects and what the move costs.
Fence: for any rule being broken, why that rule exists.
Mode field: Reception dial (Autonomous) | Advanced pole and Acceptable pole (Adaptive)
```

**2b. Make the move** in the actual artifact, then render it (screenshot, export or open it) so the panel can see it. If you cannot render, write "unrendered" in the Panel Report and say so in your final reply.

**2c. Convene the panel** on the rendered artifact.

- Composition: the required critics for your mode, chosen from the CRITICS box.
- Independence: if you have a sub-agent or task tool, run each critic as its own agent. Otherwise write each critic's report in full before reading the others, with no critic reacting to another's verdict.
- Evidence rule: every critic must point to something observable in the artifact and name one literature anchor that grounds the judgment. A critic that cites only the plan is invalid; redo it.
- Run the Critical Response Process in this order: (1) statements of meaning, what the work seems to say; (2) artist questions; (3) neutral questions from critics; (4) opinions, only after the artist permits them.
- Any critic may pull the Andon. Stop making new moves until its objection is resolved.

Panel Report format:

```
### Panel, Move N, round R  (artifact examined: <path or screenshot>)
| Critic | Anchor used | Observed in the work | Verdict PASS/OBJECT | Requested change |
Statements of meaning: ...
Artist questions: ...
Critic questions: ...
Opinions: ...
Andon pulled: yes/no, by whom
```

**2d. Resolve every OBJECT** with exactly one of:

- **ADAPT**: change the move, re-render, and re-run at least the objecting critics for as many rounds as needed. If another identical revision would repeat a failed approach, change the approach or frame and record the evidence; do not silently lower the criterion.
- **SCRAP**: revert the move and mark its Decision Record as superseded; do not delete it.
- **OVERRULE**: allowed only with a written reason citing the governing criterion of your mode. The objection stays in the log.

If 3 or more critics object to the same move or the same anchor region, stop and perform a frame swap: replace that region with a sibling anchor reached by an existing edge (dotted edges allowed) and log it as a frame swap.

**2e. Update the Anchor Ledger and the live graph** after every panel round:

```
| Anchor | Role | Status KEEP / ADAPT / SCRAP | Evidence | Replacement or note |
```

Every anchor named in any record gets a row. A KEEP must name the strongest objection it survived. Then update the graph through your graph tooling: apply `kept`, `adapted` or `scrapped` to each anchor's node id (for example, `class nodeId scrapped`), add any replacement anchor reached by an existing edge, and re-render. Without tooling, record the updated Mermaid text in the log. Scrapped anchors leave the active path for this project; this file itself is not edited. Do not write moves to please the critics' score; the governing criterion decides.

### Step 3. Expand and repeat until the work is complete

After every move and panel round, inspect the actual artifact against the entire brief and the governing criterion. Add moves for uncovered requirements, failed interactions between moves, craft defects and necessary improvements surfaced by critique. Revisit earlier moves when later changes invalidate them. Run independent branches and critics in parallel when tools permit and their changes do not conflict.

Continue Step 2 until every required deliverable is rendered and examined, every brief requirement has observable evidence, every OBJECT is resolved as ADAPT, SCRAP or a reasoned OVERRULE, and a final inspection reveals no remaining necessary move. Exhausting the initial move list, reaching a round count, or completing one part is never a Full-mode stopping condition. A high move count alone is not evidence of quality; each added move must serve the brief or resolve a witnessed defect.

If a real tool or platform limit interrupts execution, preserve the current artifact, live graph, decisions, objections and exact remaining moves in DESIGN-LOG.md and report the run as incomplete. Resume from that state when execution is available; do not call the work complete because a turn ended.

### Step 4. Close

0. **Completion inspection.** Re-render the final deliverables and inspect the entire brief, including interactions between earlier and later moves. Record the evidence for each requirement and any remaining necessary work. If work remains, return to Step 3 before closing.

1. **Double loop.** In one paragraph, say whether the criterion, the panel or the graph itself failed the work, and name one concrete amendment (a node to add or scrap, or a critic to change) under "Graph amendments".
2. **Compliance Check**, each line with a pointer to where it is satisfied:
   - [ ] Tooling inventory done; tool used for each job, or "none available"
   - [ ] Mode stated with the reason
   - [ ] Traversal Plan with exact labels, including one dotted-edge counterpoint
   - [ ] Dynamic traversal expanded until all necessary moves are complete, including a BREAK (or Lite mode stated)
   - [ ] Every brief requirement has observable evidence in the final rendered deliverables
   - [ ] Final inspection found no remaining necessary work; the initial move list and round counts were not used as stopping conditions
   - [ ] A Decision Record written before each move, with all fields filled
   - [ ] A Panel Report per round per move, from a panel meeting the mode's composition rule, each critic citing something observable
   - [ ] Every OBJECT resolved as ADAPT, SCRAP or OVERRULE
   - [ ] Anchor Ledger complete and the live graph updated
   - [ ] Double-loop paragraph written
   - [ ] Final reply states the mode, the tools used and everything skipped

## Anti-skip rules

- A commit message or code comment is not a Decision Record.
- A quick mental check or a one-line "I considered X" is not a panel.
- One move is not a traversal.
- Naming an anchor is not using it: it must appear in a record's argument or in a critic's observation, tied to something in the work.
- Not looking for graph or workflow tooling is not the same as none being available.
- Short on effort or finishing a turn is not an exemption. Continue while necessary work remains. If execution is actually interrupted, preserve the exact remaining work and report incomplete; do not shrink the brief or switch to Lite mode without the person requesting it.

## Reading the graph

Solid arrows are forward references (grounds, extends, applies). Dotted arrows are counterpoints or back-references. Boxes are clusters; an arrow into the CRITICS box means the whole panel. The Autonomous mode omits no anchors; the mode only changes the governing criterion and the required critics. Colors: amber stance, grey rules, pink breakers, violet expression, green systems, slate canon, teal reason, orange welcome, red critics, magenta lenses, cyan panel method, lime adaptation, gold autonomy of art, blue existing catalog anchors. Status classes for the live graph: `visited`, `kept`, `adapted`, `scrapped`.

## Anchor graph

Read [references/anchor-graph.md](references/anchor-graph.md) before choosing the traversal and critics. It contains the complete source graph, including all labels, edges and status classes.
