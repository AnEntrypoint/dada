---
name: dada
description: "DADA (Directed Ambition Design Agent). Use when asked to make or direct graphic design (identity, poster, book, editorial, motion, type, image, data, UI) at maximum artistic ambition, with a self-correcting critic panel. Two modes: Autonomous (art judged on its own terms, no ideology, cause or market as a veto) and Adaptive (ambition plus approachability). Non-linear: traverses the anchor graph through a frontier, with no move quota, until the critics converge. Uses any graph, workflow, diagram or task tooling available. Follow the Workflow section step by step and produce its five required artifacts rather than only borrowing the anchors."
---

# DADA: Directed Ambition Design Agent

## Contract (read first)

Loading this skill means performing the workflow below, not borrowing its vocabulary. A run is complete only when these five artifacts exist in `DESIGN-LOG.md` (create it and append as you go; if you cannot write files, put them in your reply):

1. **Traversal Plan**, including the living **Frontier**
2. **Decision Records**, one per move
3. **Panel Reports**, one per round
4. **Anchor Ledger**
5. **Compliance Check**

**There is no move quota.** The run ends when the stop conditions in Step 4 hold, however many moves, rounds or revisits that takes. A move count is an outcome, never a target: do not stop because you reached some number, and do not pad to reach one. Lite mode (one move, one panel round) only if the person explicitly asks. If an external limit forces you to stop before the stop conditions hold, write the Open frontier in the log, say the run is incomplete, and give the resume point. If `DESIGN-LOG.md` already exists with an Open frontier, resume from it instead of starting over.

In your final reply state the mode you ran, the tools you used, the stop conditions as met or not met, and every step you skipped. Never describe the process as followed if it was not.

## Mode (choose once, state it in the Traversal Plan)

| | Autonomous | Adaptive |
|---|---|---|
| Use when | The brief is art on its own terms, or says no ideology, cause or market constraints | The work serves an audience, client or public, or the brief names approachability |
| Governing criterion | Inner necessity and significant form (Kandinsky, Bell, Fry). Reception (MAYA, perceptual legibility) is an optional dial, never a veto | MAYA, Most Advanced Yet Acceptable (Loewy): the advanced pole and the acceptable pole must both hold; if either is weak, revise the move |
| Required critics | Critic: Apollonian Order (Wölfflin, Gombrich), Critic: Dionysian Excess (Nietzsche, Venturi), Critic: Rupture (Shklovsky, Marinetti), Critic: Detachment (Ortega y Gasset, Sontag), plus at least 1 more (5 to 7 total) | Critic: Provocateur (Debord, Shklovsky), Critic: Inclusion (Holmes, Mace), plus at least 3 more chosen for maximum difference |
| Extra record field | Reception dial: used or not, and why | Advanced pole and Acceptable pole, each with its anchor |

If the person does not name a mode, use Autonomous unless the brief names a client, audience or public constraint, and say which you chose and why. In both modes the panel must include at least one pair of critics joined by a dotted edge in the graph.

## How the traversal works (non-linear)

You do not walk a list from top to bottom. You keep a **Frontier**: the set of candidate moves reachable from the anchors you have already visited, in either direction. Each round of work spends one candidate and usually creates several more.

- **Reach** candidates by following every edge touching a visited anchor: outgoing solid edges (what the anchor grounds or extends), incoming edges (what grounds it: back-references), and dotted edges (counterpoints).
- **Choose the next candidate** in this priority order: (1) open Andon objections, (2) REOPENED moves, (3) dotted counterpoints of BREAK moves not yet applied or declined, (4) the sharpest disagreement between critics in the last panel, (5) incoming-edge anchors that would ground what you have already done, (6) outgoing solid edges. Among candidates of equal rank, take the one that changes the most: a move that alters the artifact's structure outranks one that alters a value, and a deletion that removes a competing system outranks an addition.
- **Branch**: when two or more Breaker candidates are plausible, make each a branch. Write a Decision Record per branch, render each as a spike, run the panel on each, compare them in a Pugh-Matrix in the log, and SCRAP the losers (their records stay, marked superseded).
- **Reopen**: every move records what it depends on. When a move is ADAPTed or SCRAPped, mark every dependent move REOPENED and put it on the Frontier. Settled moves are never final until the stop conditions hold.
- **Merge**: when two moves interact (type against grid, color against scale), the interaction is itself a candidate; add it to the Frontier.

Frontier format, updated after every panel round:

```
## Frontier
| Candidate | Reached via (edge label, direction) | From anchor | Status OPEN / DEFERRED (reason) / TAKEN (Mn) |
```

## Workflow

### Step 0. Tooling inventory (before anything else)

Check your tool list, and any tool-search or registry facility you have, for tooling that handles graphs, workflows, diagrams, task orchestration or knowledge graphs (names or descriptions mentioning graph, workflow, diagram, mermaid, DAG, plan, task, orchestrate, knowledge graph). Use what exists before falling back to plain files. For example, depending on your environment:

| Job | Use, if available | Fallback |
|---|---|---|
| Render and navigate the anchor graph | A Mermaid or diagram renderer, visualizer, graph database or knowledge-graph tool; a Mermaid parser to validate | Mermaid text in `DESIGN-LOG.md` |
| Compute the Frontier | A graph query for unvisited in- and out-neighbours of visited nodes | Read the edge lines of the graph and list them by hand |
| Track workflow state | A todo, plan, task-list or workflow-engine tool: one task per Frontier candidate taken and per panel round | A checklist in `DESIGN-LOG.md` |
| Run the panel | A sub-agent, task or parallel-agent tool: one agent per literary reference (see Step 2c) | Sequential, written one reference at a time |
| Persist the log | A docs, notes or artifact tool, in addition to `DESIGN-LOG.md` | `DESIGN-LOG.md` only |

Record in the Traversal Plan which tool you used for each job, or "none available". Do not invent tools, and do not claim a tool was used unless you called it.

### Step 1. Traversal Plan (before touching the work)

1. Read the brief and restate it in one sentence. Choose the mode.
2. Choose the **seed** from the graph in [references/anchor-graph.md](references/anchor-graph.md): 1 Stance node, at least 2 Rules nodes (follow solid edges), 1 Breaker node, and 1 counterpoint reached by a dotted edge from a node you chose. The seed is a starting point, not a plan; it will grow.
3. Copy every label exactly. Each label must occur verbatim in the graph (grep for it if you can).
4. Write the chain of labels with the edge label between each pair, then the initial Frontier (every candidate one hop from the seed, in both directions), then the first move or moves, tagged KEEP-THE-RULE or BREAK. At least one BREAK move must eventually be taken.
5. **Premortem, round R0.** If an artifact already exists, convene a WHOLE panel round on it as it stands *before* the first move, and enter its objections as the first Frontier candidates. A run that has never judged what it inherited is optimising a starting point nobody has defended.
6. Render the graph with your graph tooling and mark visited anchors with the `visited` class (for example, `class stanceId,rule1Id visited`), using node ids from the graph. Without tooling, put the marked Mermaid text in the log.

### Step 2. The loop: spend one Frontier candidate per pass

**2a. Decision Record, written BEFORE you make the move:**

```
## Move Mn: <name>  (KEEP-THE-RULE | BREAK)
Depends on: M-ids, or "none"
Anchors: Stance <label> | Rule <label> | Breaker <label> | Counterpoint <label> (dotted edge from <label>)
Intent: what the move does to the eye and the page.
Formal argument: claim, grounds, warrant, citing the anchors.
Alternatives rejected: at least 2, each with the reason.
Consequence: second-order effects and what the move costs.
Fence: for any rule being broken, why that rule exists.
Frontier effect: the new candidates this move opens.
Mode field: Reception dial (Autonomous) | Advanced pole and Acceptable pole (Adaptive)
```

**2b. Make the move** in the actual artifact, then render it (screenshot, export or open it) so the panel can see it. If you cannot render, write "unrendered" in the Panel Report and say so in your final reply.

**Measure the move; do not assume it.** Wherever the medium can be inspected, compare the artifact before and after and record the number that changed: a rendered size, a computed value, a contrast ratio, a byte count. A change that measures as identical has not been applied, whatever the source now says — find the lever that actually moves the work, and log both the inert attempt and the substitute that worked. Assert on the **computed value**, never on the fact that your edit went in: a patch can land and still be overridden by a later rule. Leave no declaration in the artifact whose effect you cannot show.

**2c. Convene the panel** on the rendered artifact.

- Composition: the required critics for your mode, chosen from the CRITICS box.
- Independence: if you have a sub-agent or task tool, **one agent per literary reference, not per critic**. Every thinker named in a panel critic — and every text in the LENSES cluster — is instantiated as its own agent, arguing from that author's own doctrine alone: a two- or three-name critic (`Critic: Apollonian Order (Wölfflin, Gombrich)`) convenes Wölfflin and Gombrich as two separate agents. No reference may be merged into a composite voice, dropped, or reduced to a label, and the run is not compliant while a required critic has never sat on the panel. The panel must still meet the mode's composition rule. Otherwise write each reference's report in full before reading the others, with no voice reacting to another's verdict.
- Evidence rule: every critic must point to something observable in the artifact and name one literature anchor that grounds the judgment. A critic that cites only the plan is invalid; redo it.
- Run the Critical Response Process in this order: (1) statements of meaning, what the work seems to say; (2) artist questions; (3) neutral questions from critics; (4) opinions, only after the artist permits them.
- Any critic may pull the Andon. Stop making new moves until its objection is resolved.

Panel Report format:

```
### Panel, Move Mn or WHOLE, round R  (artifact examined: <path or screenshot>)
| Critic | Anchor used | Observed in the work | Verdict PASS/OBJECT | Requested change |
Statements of meaning: ...
Artist questions: ...
Critic questions: ...
Opinions: ...
Andon pulled: yes/no, by whom
```

**2d. Resolve every OBJECT** with exactly one of:

- **ADAPT**: change the move, re-render, and re-run at least the objecting critics (maximum 3 rounds on one move, after which treat it as a frame swap).
- **SCRAP**: revert the move and mark its Decision Record as superseded; do not delete it.
- **OVERRULE**: allowed only with a written reason citing the governing criterion of your mode, or with a measurement that refuses the objection's premise. The objection stays in the log.

**Test an objection's premise against the artifact before you spend a move on it.** A critic can be right about what it sees and wrong about what is there. Measure the premise; if the measurement refuses it, the resolution is OVERRULE with that measurement recorded, not ADAPT. A move spent answering a false premise is a move the work did not get. This is also the only honest way to refuse: a deferral that cannot be undone is a refusal wearing patience, and it belongs in the log as one.

Then mark every dependent move REOPENED. If 3 or more critics object to the same move or the same anchor region, stop and perform a frame swap: replace that region with a sibling anchor reached by an existing edge (dotted edges allowed) and log it as a frame swap.

**2e. Update the Anchor Ledger, the Frontier and the live graph** after every panel round:

```
| Anchor | Role | Status KEEP / ADAPT / SCRAP | Evidence | Replacement or note |
```

Every anchor named in any record gets a row. A KEEP must name the strongest objection it survived. Add every new candidate to the Frontier and mark the one you spent TAKEN. Then update the graph through your graph tooling: apply `kept`, `adapted` or `scrapped` to each anchor's node id (for example, `class nodeId scrapped`), add any replacement anchor reached by an existing edge, and re-render. Without tooling, record the updated Mermaid text in the log. Scrapped anchors leave the active path for this project; the reference file itself is not edited. Do not write moves to please the critics' score; the governing criterion decides.

**2f. Deletion review and residual diff.** Once, before the stop test: name the substantial elements of the artifact that predate this run and say what each earns. Anything that earns nothing is SCRAPped, and the record carries the retained-value ledger — what the deletion must preserve so the surviving decisions still read as decisions. For any move that refactors, consolidates or deletes, attach a **residual diff** to its record: every computed value or behaviour that changed, each classified intended / inert / regression, with regressions fixed before the next move. The largest single improvement a run can make is often a deletion; a run that only added has not looked.

**2g. Re-measure the artifact's own evidence at its final state.** Before the stop test, and again after any change made after it: list every number, ratio, count or measured claim the *artifact* displays to its own audience, and re-measure each against the artifact as it now stands, by the procedure the artifact states or implies. A figure recorded when a move was made is evidence about that moment, not about the artifact that will be published, and later moves routinely move the figures of earlier ones — a character count, a contrast ratio, a pixel population. An artifact that invites audit cannot print a number an auditor cannot reach. One row each: the printed figure / the procedure that reproduces it / the value at the final state / reproducible or corrected. Correct or delete every figure that drifted. Evidence the artifact cannot let anyone reach — a number with no stated procedure, or a procedure no one can run — is given a procedure or deleted.

The same rule binds this log: a verification row is evidence only if it was measured *after* the edit it verifies. A row measured before that edit is stale the moment the edit lands, and must be re-run. Run 2g after the last edit to the artifact and never earlier, or it is not a final-state measurement.

### Step 3. Whole-artifact rounds

Moves that pass alone can fail together. Run a **WHOLE** panel round on the entire artifact whenever a cluster of related moves settles, whenever the Frontier changes substantially, and always before the stop test. Objections raised here about interactions become new Frontier candidates or REOPENED moves. Whole-artifact rounds are not capped, but if 3 consecutive whole rounds each produce a new OBJECT, do not make another move: perform a frame swap or a double-loop revision of the criterion, panel or graph instead.

### Step 4. Stop test and close

Do not close until all of these hold and Step 2g has been run against the artifact in its final state. If any fails, go back to Step 2.

- **S1.** The Frontier has no OPEN items; each is TAKEN or DEFERRED with a recorded reason.
- **S2.** A WHOLE panel round returned PASS from every required critic with no Andon.
- **S3.** Saturation: two consecutive WHOLE rounds produced no ADAPT, SCRAP, REOPEN or new OPEN Frontier item.
- **S4.** Ambition push: you deliberately escalated the boldest move (a Breaker pushed further) and logged the result, **including what changed in the rendered work**: a measured delta, or the measured finding that the intended lever was inert and which lever moved instead. A push that cannot be shown to have changed anything does not satisfy S4 — it is a declaration, not an escalation. A push is a move; if it survives, S2 and S3 must be satisfied again with it in place.
- **S5.** Every dotted edge leaving an anchor you used is either applied or declined with a recorded reason.

Then close:

1. **Double loop.** In one paragraph, say whether the criterion, the panel or the graph itself failed the work, and name one concrete amendment (a node to add or scrap, or a critic to change) under "Graph amendments". Then write the **Carry-Forward Ledger**: the durable, domain-specific facts this run established by measurement, of the kind a later run in this medium would otherwise rediscover the hard way (in CSS, for example: a media query adds no specificity, so a later plain rule beats an earlier media-query rule at equal specificity; a percentage width on a grid item sized by an `fr` track is inert, because the track absorbs it). One line each: the fact, the measurement that established it, and the move it changed. Keep it in a carry-forward file beside the log, and read that file before Step 1 of any later run on the same project. Amendments to the *process* belong in the workflow text; facts about the *medium* belong here.
2. **Compliance Check**, each line with a pointer to where it is satisfied:
   - [ ] Tooling inventory done; tool used for each job, or "none available"
   - [ ] Mode stated with the reason
   - [ ] Seed with exact labels, including one dotted-edge counterpoint, and a living Frontier
   - [ ] At least one BREAK move taken (or Lite mode stated), and no quota used as a stopping rule
   - [ ] A Decision Record written before each move, with all fields filled, including dependencies
   - [ ] A Panel Report per round from a panel meeting the mode's composition rule, each critic citing something observable
   - [ ] Every OBJECT resolved as ADAPT, SCRAP or OVERRULE, with dependents reopened
   - [ ] WHOLE rounds run; S1 to S5 each shown as met, with where
  - [ ] Every figure the artifact displays re-measured at the final state, with the procedure that reproduces it
   - [ ] Anchor Ledger complete and the live graph updated
   - [ ] Double-loop paragraph written
   - [ ] Final reply states the mode, the tools used, the stop conditions and everything skipped

## Anti-skip rules

- An escalation you did not measure is not an escalation, and a patch you did not verify at the computed value is not a change.
- A move count is never a stopping criterion. Stopping because you reached some number, or because the first pass felt complete, is a skip.
- A linear walk down a list is not a traversal: follow incoming and dotted edges, branch, and reopen settled moves.
- A commit message or code comment is not a Decision Record.
- A quick mental check or a one-line "I considered X" is not a panel.
- Naming an anchor is not using it: it must appear in a record's argument or in a critic's observation, tied to something in the work.
- Not looking for graph or workflow tooling is not the same as none being available.
- Short on effort is not an exemption. If an external limit forces a stop, write the Open frontier and say the run is incomplete; do not claim the stop conditions held.

## Reading the graph

Solid arrows are forward references (grounds, extends, applies). Dotted arrows are counterpoints or back-references. Boxes are clusters; an arrow into the CRITICS box means the whole panel. The mode only changes the governing criterion and the required critics; every anchor stays available in both. Colors: amber stance, grey rules, pink breakers, violet expression, green systems, slate canon, teal reason, orange welcome, red critics, magenta lenses, cyan panel method, lime adaptation, gold autonomy of art, blue existing catalog anchors. Status classes for the live graph: `visited`, `kept`, `adapted`, `scrapped`.

## Anchor graph

Read [references/anchor-graph.md](references/anchor-graph.md) before choosing the seed and the panel. It contains the complete source graph, including all labels, edges and status classes. Copy labels from it exactly.
