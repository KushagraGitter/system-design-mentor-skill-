#!/usr/bin/env python3
"""Real-clock timer for mock system design interviews.

The chat has no clock of its own, so the interviewer runs `check` on every turn to know how much
time has passed, which phase the candidate *should* be in, and whether to interrupt.

  mock.py start --problem news-feed [--minutes 45] [--level senior]
  mock.py phase deep-dives        # the candidate moved on (records when)
  mock.py check                   # elapsed, expected phase, drift, and an interrupt cue if due
  mock.py end                     # final timing summary (paste into the review)

State: <state dir>/mock.json (same folder as progress.json; --dir or $SD_MENTOR_DIR).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
from pathlib import Path

# share of the session per phase (sums to 1.0) — the 45-minute shape from study-plans.md
PHASES = [
    ("requirements", 0.11, "functional + non-functional requirements, scope cuts"),
    ("entities-api", 0.16, "core entities and API"),
    ("high-level", 0.33, "high-level design that satisfies every functional requirement"),
    ("deep-dives", 0.33, "deep dives against the non-functional requirements"),
    ("wrap-up", 0.07, "bottlenecks, what you'd do next, questions"),
]
NAMES = [p[0] for p in PHASES]
ALIASES = {"reqs": "requirements", "requirement": "requirements", "api": "entities-api",
           "entities": "entities-api", "hld": "high-level", "design": "high-level",
           "deep": "deep-dives", "deepdive": "deep-dives", "wrap": "wrap-up", "end": "wrap-up"}


def now() -> dt.datetime:
    o = os.environ.get("SD_MENTOR_NOW")  # for testing: ISO timestamp
    return dt.datetime.fromisoformat(o) if o else dt.datetime.now(dt.timezone.utc)


def path(args) -> Path:
    return Path(args.dir or os.environ.get("SD_MENTOR_DIR") or "sd-mentor") / "mock.json"


def load(args):
    p = path(args)
    if not p.exists():
        sys.exit("No mock in progress. Start one with `mock.py start --problem <id>`.")
    return json.loads(p.read_text())


def save(args, m):
    p = path(args)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(m, indent=2))


def schedule(minutes):
    """[(name, start_min, end_min, desc)]"""
    out, t = [], 0.0
    for name, share, desc in PHASES:
        out.append((name, round(t, 1), round(t + share * minutes, 1), desc))
        t += share * minutes
    return out


def elapsed_min(m) -> float:
    return (now() - dt.datetime.fromisoformat(m["started"])).total_seconds() / 60


def current_phase(m):
    return m["phase_log"][-1]["phase"] if m["phase_log"] else "requirements"


def cmd_start(args):
    p = path(args)
    if p.exists() and not args.force:
        m = json.loads(p.read_text())
        if not m.get("ended"):
            sys.exit(f"A mock for '{m['problem']}' is already running ({elapsed_min(m):.0f} min in). "
                     f"`end` it first, or pass --force.")
    m = {"problem": args.problem, "minutes": args.minutes, "level": args.level,
         "started": now().isoformat(), "phase_log": [{"phase": "requirements", "at": 0.0}],
         "interrupts": [], "ended": None}
    save(args, m)
    print(f"Mock started: {args.problem}, {args.minutes} min, {args.level} level.")
    for name, a, b, desc in schedule(args.minutes):
        print(f"  {a:>4.0f}–{b:<4.0f} min  {name:<13} {desc}")


def cmd_phase(args):
    m = load(args)
    name = ALIASES.get(args.name, args.name)
    if name not in NAMES:
        sys.exit(f"Unknown phase '{args.name}'. Use one of: {', '.join(NAMES)}")
    at = round(elapsed_min(m), 1)
    m["phase_log"].append({"phase": name, "at": at})
    save(args, m)
    print(f"{name} at {at:.0f} min")


def cmd_check(args):
    m = load(args)
    e = elapsed_min(m)
    total = m["minutes"]
    sched = schedule(total)
    expected = next((s for s in sched if s[1] <= e < s[2]), sched[-1])
    actual = current_phase(m)
    a_idx, x_idx = NAMES.index(actual), NAMES.index(expected[0])
    actual_end = next(s[2] for s in sched if s[0] == actual)
    over = e - actual_end
    remaining = total - e
    print(f"Elapsed {e:.0f} of {total} min · {max(0, remaining):.0f} min left")
    print(f"Candidate is in: {actual} · schedule says: {expected[0]}")
    cue = None
    if remaining <= 0:
        cue = "Time is up. Stop the candidate, ask for the final diagram, and grade."
    elif a_idx < x_idx and over >= 2:
        nxt = NAMES[a_idx + 1]
        cue = (f"Interrupt: {over:.0f} min over on {actual}. Ask them to move to {nxt} "
               f"(e.g. \"Let's park that — can you sketch the {nxt.replace('-', ' ')} now?\").")
    elif remaining <= 5 and actual != "wrap-up":
        cue = "Interrupt: 5 minutes left. Ask for the biggest remaining bottleneck and what they'd do next."
    elif actual == "deep-dives" and not any(i.get("kind") == "probe" for i in m["interrupts"]) and e >= sched[3][1] + 5:
        cue = ("Probe: they've had 5+ minutes of deep dives. Push on the problem's hard part "
               "(see its Deep dives line) or kill a component and ask what happens.")
    if cue:
        kind = "probe" if cue.startswith("Probe") else "time"
        m["interrupts"].append({"at": round(e, 1), "kind": kind, "cue": cue})
        save(args, m)
        print(cue)
    else:
        print("No interrupt needed — let them drive.")


def cmd_end(args):
    m = load(args)
    e = elapsed_min(m)
    m["ended"] = now().isoformat()
    m["phase_log"].append({"phase": "end", "at": round(e, 1)})
    save(args, m)
    planned = {s[0]: s[2] - s[1] for s in schedule(m["minutes"])}
    print(f"Mock '{m['problem']}' ended at {e:.0f} min (planned {m['minutes']}).")
    print("Phase timing (actual vs planned):")
    log = m["phase_log"]
    spent = {}
    for cur, nxt in zip(log, log[1:]):
        spent[cur["phase"]] = spent.get(cur["phase"], 0) + (nxt["at"] - cur["at"])
    for name in NAMES:
        a = spent.get(name, 0)
        flag = ""
        if a == 0:
            flag = "  ← skipped"
        elif a > planned[name] * 1.3 and a - planned[name] >= 3:
            flag = "  ← ran long"
        print(f"  {name:<13} {a:>5.1f} min vs {planned[name]:>4.1f}{flag}")
    if m["interrupts"]:
        print(f"Interrupts: {len(m['interrupts'])} ({', '.join(i['kind'] for i in m['interrupts'])})")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dir")
    sp = ap.add_subparsers(dest="cmd", required=True)
    s = sp.add_parser("start"); s.add_argument("--problem", required=True)
    s.add_argument("--minutes", type=int, default=45)
    s.add_argument("--level", default="senior", choices=["junior", "mid", "senior", "staff"])
    s.add_argument("--force", action="store_true"); s.set_defaults(fn=cmd_start)
    s = sp.add_parser("phase"); s.add_argument("name"); s.set_defaults(fn=cmd_phase)
    s = sp.add_parser("check"); s.set_defaults(fn=cmd_check)
    s = sp.add_parser("end"); s.set_defaults(fn=cmd_end)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
