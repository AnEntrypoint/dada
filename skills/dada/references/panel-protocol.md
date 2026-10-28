# Panel protocol: how a round is convened so no verdict is lost

A panel round is several independent agents run at once, and the harness that
runs them is not reliable. A seat can be launched, do all its work, write its
verdict — and have the connection drop before the verdict reaches the caller.
When that happens the caller sees "failed" and the work is gone.

This is not rare. In one Adaptive run using this skill, seven seats were
launched in a single batch: five of them died with a gateway error and had to
be re-run, and the two that landed first time were the two with the shortest
prompts. The failure is in the transport, not in the doctrine. The protocol
below assumes it will happen again and makes the verdict survive it.

## The rule

**A verdict is a file, not a return value.** A seat has reported when its file
exists. Nothing else counts — not the launch call, not a completion notice, not
anything the caller remembers seeing.

## What the caller does

1. **Make a panel directory before launching anything.** One per round is
   clearest: `panel/R1/`, `panel/R2/`. It is the round's state, so a session
   that restarts can be resumed by listing it instead of re-running everything.

2. **Launch at most three seats at a time.** Launching seven, or even four,
   produced five transport failures in the run above; batches of three with
   short prompts did not fail. A panel of seven is three batches, and the wall
   clock is barely worse because the batches are short.

3. **Keep the seat prompt under about 350 words.** The seats that survived
   repeated failures were the ones whose prompts had been trimmed to the
   evidence pointer, the seat, and the four required output fields. Give the
   seat a file of measured facts to read rather than paraphrasing the artifact
   into the prompt.

4. **Every seat prompt ends with the filing instruction**, naming the absolute
   path:

   > Write your report to `<panel_dir>/<seat>.md` as your last action, then
   > return the same text. If the connection drops, the file is the verdict.

5. **Before re-running a failed seat, check whether its file exists.** A dropped
   agent has usually already written it. Re-running a seat whose verdict is on
   disk wastes the seat and risks two conflicting verdicts under one name.

6. **Bound the retries: three attempts per seat.** After that, stop.

7. **Collect, then write the Panel Report.** List the directory and read what
   is there. A required seat with no file is recorded as
   `NOT REPORTED (3 attempts, transport failure)` — never as PASS, never
   reconstructed from what the caller thinks that authority would have said.
   A required seat that never reports leaves the run incomplete, and the final
   reply says so and names the seat.

## What the seat prompt needs

- Which round and which seat, and the doctrine it argues from alone.
- Where the artifact is, and where the measured evidence file is.
- The four required fields: Anchor used / Observed / Verdict / Requested change.
- The word budget.
- The instruction not to read or react to any other seat.
- The filing instruction, with the path.

Nothing else. Everything else belongs in a file the seat reads.

## Collector

`scripts/collect_panel.py` lists which seats reported and which did not:

```bash
python scripts/collect_panel.py panel/R1 debord shklovsky holmes mace krug sharp bringhurst
```

It prints `REPORTED` or `MISSING` per seat with a word count, refuses to treat
an empty or near-empty file as a verdict, and exits non-zero if any seat is
missing so a retry loop can drive off it.

## Why the file wins

The five failures above each cost a full seat: re-running meant reading the
artifact again from the start, and one seat needed three attempts. Had the
seats filed their verdicts, four of the five would have needed no re-run at
all — the file would have been there when the caller looked.
