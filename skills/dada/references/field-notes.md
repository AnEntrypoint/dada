# Field notes: what has actually worked in Adaptive runs

Distilled from the runs that produced the strongest artifacts — UGC Events &
Media, WTF, Copperline Plumbing, Highwater Rafting — and from what failed in
them. Each note says where it came from so it can be checked, and each is a
thing to *do*, not a thing to admire.

Read alongside [the panel protocol](panel-protocol.md).

---

## 1. MAYA resolves the Sharp ↔ Shklovsky conflict by address, not by compromise

The recurring split on a public-facing site is Sharp (recognition, deploy the
asset identically everywhere) against Shklovsky (estrangement, do not let the
device become furniture). Both are right, and splitting the difference produces
a site that is half-strange everywhere and memorable nowhere.

**Resolve it by address.** Put the break on the home page and recognition on
every other page. UGC did this: the cut-paper hero lives on the index, the
inner pages are conventionally navigable. Both critics accepted it in writing
(UGC R2 Frontier). Highwater did the same — the gauge is the home page's
display head; trips, guides, safety and basecamp are plain.

Record the resolution in the Frontier, not just in the prose.

## 2. Enroll a measurement seat, because the panel does not measure by default

This is the largest failure found across these runs. In UGC, the two most
serious defects — text contrast over a photograph, and a focus ring clipped
away by `clip-path` — were found by measurement scripts, **not by any critic**.
No seat measured anything unprompted except Mace. Several critics judged from
two or three screenshots when the run had captured six.

So: for any artifact that can be inspected, convene `Critic: Evidence (Cairo)`
as a required Adaptive seat, briefed to *run measurements* — contrast over
images, focus visibility, overflow, target size, link inventory — rather than
to read screenshots. And give Mace a named focus-visibility check.

The corollary, from the Highwater run, is the instrument check: a finding that
appears only in a tool's output must be measured on the rendered page before a
move is spent on it. Two of that run's "failures" were artefacts of the
contrast sampler and of a local static server not running `cleanUrls`.

## 3. The seeded Breaker earns its place only when escalated

S4 asks for an ambition push. It should be an escalation of the Breaker you
already seeded, not a new device bolted on beside it. UGC seeded `Saul Bass: A
Life in Film and Design`, took the cut-paper ridgeline as M3, and pushed it in
M8 to the photograph cut into the mountain — the same idea, harder. Highwater
seeded `Making and Breaking the Grid`, took the flow axis as M2, and pushed it
to a draggable gauge that recomputes every trip state.

An escalation that does not change a measured number is a declaration. Both of
the above logged deltas (hero text 2.0 → 5.1:1; trip states `on,on,on,over,on,on`
→ all six open when the reading moves).

## 4. One generator, and put the guarantees in the build

Every one of these sites that survived later editing is
`_src/build.py` + `_src/layout.html` + `_src/pages/*.html`, with
`_src/data/*.json` wherever a fact is printed more than once. Two payoffs, both
earned the hard way:

- **A fact printed twice will drift.** Highwater's favicon used one vermilion
  and the stylesheet another; the fix was to make the build *write* the favicon
  from the stylesheet's tokens so the colour is typed once.
- **The build is where a guarantee can live.** Highwater's build refuses to
  emit a page whose internal links point at a file it did not write, so a dead
  link fails at build time rather than in a browser. This is what closes
  Debord's standard objection (an image of a business with no referent) in a
  way a critic can verify rather than take on trust.

## 5. The highest-value late moves are deletions of claims

Late in a run, once the form is good, the moves that most improve the work are
removals:

- UGC M13: remove every claim the owner has not made.
- UGC M5 (Redish): copy of fact, not slogans.
- Highwater M6: a June gauge reading printed in October must not say "running".

Debord, Cairo and Redish all converge here, and each time the objection arrived
late because the claim only became visible once the page was worth reading.
Budget a late move for this and expect it.

**Rule of thumb:** every claim the artifact prints needs a source in the repo.
If the source does not exist, either the claim comes out or the artifact says
on its face that it is a placeholder — a concept site whose phone number is a
555 number and whose email uses `.example` is honest; one that prints "Book
now" over a form with no endpoint is not.

## 6. Batching is the honest deviation — record it

Every one of these runs wrote Decision Records in batches before each group of
moves, and ran the panel per WHOLE round rather than per move. The contract
asks for one at a time. Do not pretend otherwise: write the deviation into the
Compliance Check, as UGC did. A fabricated one-at-a-time compliance line is
worse than an admitted batch.

## 7. Deferrals to the owner belong in S1, and on the artifact's face

Owner-dependent gaps — a real email address, capacity figures, a phone number,
footage — are not OPEN Frontier items and not defects. List them under S1 with
the reason, and make the artifact say what it does not have rather than
implying it does. The portfolio run marked a mailto slot in the template and
said in the page that a direct address was on its way; that is the pattern.

## 8. Grow the graph while you run

UGC seeded 6 anchors and closed with 22 in the ledger — Krug, Redish, Berger,
Holmes, Nielsen, Yablonski, Beier, Cairo, Gestalt, Wheeler all arrived because
a move or an objection needed them. The seed is a starting point. Enroll an
anchor only when it does work in a record's argument or in a critic's
observation, and give it a ledger row when you do.
