"""List which panel seats have reported and which have not.

    python scripts/collect_panel.py <panel_dir> <seat> [<seat> ...]

A verdict is a file. A seat has reported when <panel_dir>/<seat>.md exists and
actually says something. This script never infers a verdict and never treats a
missing seat as a pass: it prints MISSING and exits non-zero, so a caller can
retry the seat or record it as NOT REPORTED.

Usage in a round:
    python scripts/collect_panel.py panel/R1 debord shklovsky holmes
    # ... retry whatever printed MISSING, then run it again
"""
import pathlib
import sys

MIN_WORDS = 20  # a verdict names an anchor and points at the work; 20 words cannot


def main(argv):
    if len(argv) < 3:
        print(__doc__.strip(), file=sys.stderr)
        return 2

    panel = pathlib.Path(argv[1])
    seats = argv[2:]
    missing, empty = [], []

    for seat in seats:
        f = panel / f"{seat}.md"
        if not f.is_file():
            print(f"MISSING  {seat}")
            missing.append(seat)
            continue
        words = len(f.read_text(encoding="utf-8", errors="replace").split())
        if words < MIN_WORDS:
            print(f"EMPTY    {seat}  ({words} words — under {MIN_WORDS})")
            empty.append(seat)
        else:
            print(f"REPORTED {seat}  ({words} words)")

    bad = missing + empty
    print(f"\n{len(seats) - len(bad)} of {len(seats)} seats reported.")
    if bad:
        print("not reported: " + ", ".join(bad))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
