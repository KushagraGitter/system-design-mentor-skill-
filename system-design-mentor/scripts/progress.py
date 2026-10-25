#!/usr/bin/env python3
"""System design mentor — plan + progress tracker (stdlib only).

State lives in a folder (default ./sd-mentor, override with --dir or SD_MENTOR_DIR):
  progress.json   machine state (source of truth)
  progress.md     human-readable report, regenerated on every write
  submissions/    copies of graded diagrams, named <problem>-attempt<n>.<ext>

Commands
  init      create a study plan          status    one-screen summary
  next      what to do now               topic     update a topic (learning/done/skipped + quiz)
  review    record a spaced-repetition review           grade     record a graded assignment
  log       log study time               report    regenerate progress.md
  topics    list topics with status      problems  list problems (--eligible for unlocked ones)
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
TOPICS_FILE = SKILL_DIR / "assets" / "topics.json"
PROBLEMS_FILE = SKILL_DIR / "references" / "problems.md"
PASS_SCORE = 70
REVIEW_INTERVALS = [1, 3, 7, 21, 60]  # days between spaced reviews
RUBRIC_KEYS = ["req", "est", "api", "arch", "deep", "tradeoff", "rel", "clarity"]
RUBRIC_TOPICS = {  # weak rubric dimension -> topics to revisit
    "req": ["fundamentals", "interview-framework"],
    "est": ["estimation"],
    "api": ["api-design", "data-modeling"],
    "tradeoff": ["tradeoff-communication"],
    "rel": ["reliability", "availability-dr"],
    "clarity": ["interview-framework"],
    # arch/deep map to the problem's own topics (added at grade time)
}
LEVEL_ORDER = {"L1": 1, "L2": 2, "L3": 3}


# ---------------------------------------------------------------- helpers
def today() -> dt.date:
    override = os.environ.get("SD_MENTOR_TODAY")  # for testing
    return dt.date.fromisoformat(override) if override else dt.date.today()


def load_catalog():
    data = json.loads(TOPICS_FILE.read_text())
    topics = {t["id"]: t for t in data["topics"]}
    phases = {p["id"]: p["title"] for p in data["phases"]}
    return data["topics"], topics, phases


def load_problems():
    """Parse references/problems.md: '### id — Title' + 'Level:' + 'Topics:' lines."""
    problems, cur = [], None
    for line in PROBLEMS_FILE.read_text().splitlines():
        m = re.match(r"^###\s+([a-z0-9-]+)\s+[—-]+\s+(.+)$", line)
        if m:
            cur = {"id": m.group(1), "title": m.group(2).strip(), "level": "L2", "topics": []}
            problems.append(cur)
        elif cur and line.startswith("Level:"):
            cur["level"] = line.split(":", 1)[1].strip()
        elif cur and line.startswith("Topics:"):
            cur["topics"] = [t.strip() for t in line.split(":", 1)[1].split(",") if t.strip()]
    return problems


def state_dir(args) -> Path:
    return Path(args.dir or os.environ.get("SD_MENTOR_DIR") or "sd-mentor")


def load_state(args) -> dict:
    p = state_dir(args) / "progress.json"
    if not p.exists():
        sys.exit(f"No progress found at {p}. Run `progress.py init` first (or pass --dir).")
    return json.loads(p.read_text())


def save_state(args, st: dict):
    d = state_dir(args)
    d.mkdir(parents=True, exist_ok=True)
    st["updated"] = today().isoformat()
    (d / "progress.json").write_text(json.dumps(st, indent=2))
    (d / "progress.md").write_text(render_report(st))


def topo_order(catalog, include):
    """Prerequisite-respecting order, stable w.r.t. catalog order."""
    ids = [t["id"] for t in catalog if t["id"] in include]
    by_id = {t["id"]: t for t in catalog}
    done, out = set(), []
    while len(out) < len(ids):
        progressed = False
        for i in ids:
            if i in done:
                continue
            if all(p in done or p not in include for p in by_id[i]["prereqs"]):
                out.append(i)
                done.add(i)
                progressed = True
        if not progressed:  # cycle guard
            out += [i for i in ids if i not in done]
            break
    return out


def week_of(st) -> int:
    start = dt.date.fromisoformat(st["profile"]["start"])
    return max(1, (today() - start).days // 7 + 1)


# ---------------------------------------------------------------- init
def cmd_init(args):
    d = state_dir(args)
    if (d / "progress.json").exists() and not args.force:
        sys.exit(f"{d/'progress.json'} already exists. Use --force to start over.")
    catalog, topics, _ = load_catalog()
    problems = load_problems()

    tracks = {"core"}
    if args.goal in ("real-world", "both") or args.level in ("senior", "staff"):
        tracks.add("depth")
    if args.include_optional:
        tracks.add("optional")
    include = {t["id"] for t in catalog if t["track"] in tracks}
    include |= set(_csv(args.add_topics))
    include -= set(_csv(args.skip_topics))
    known = set(_csv(args.known))

    order = topo_order(catalog, include)
    weeks = max(1, args.weeks)
    budget = args.hours_per_week
    practice_share = 0.35 if args.goal != "real-world" else 0.25
    learn_budget = budget * (1 - practice_share)

    # spread topics across the first ~80% of weeks; last weeks are practice/mock heavy
    learn_weeks = max(1, round(weeks * 0.8)) if weeks > 2 else weeks
    todo = [t for t in order if t not in known]
    total_h = sum(topics[t]["hours"] for t in todo) or 1
    per_week_h = max(learn_budget, total_h / learn_weeks)
    plan, wk, acc = [], 1, 0.0
    buckets = {w: [] for w in range(1, weeks + 1)}
    for t in todo:
        h = topics[t]["hours"]
        if acc + h > per_week_h * 1.15 and buckets[wk] and wk < learn_weeks:
            wk, acc = wk + 1, 0.0
        buckets[wk].append(t)
        acc += h

    # assign problems once all their (included) topics are scheduled
    scheduled_by = {}
    for w in range(1, weeks + 1):
        for t in buckets[w]:
            scheduled_by[t] = w
    for t in known:
        scheduled_by[t] = 0
    max_level = {"junior": 2, "mid": 2, "senior": 3, "staff": 3}[args.level]
    prob_week = {}
    for p in sorted(problems, key=lambda p: LEVEL_ORDER.get(p["level"], 2)):
        if LEVEL_ORDER.get(p["level"], 2) > max_level:
            continue
        needed = [scheduled_by.get(t, 0) for t in p["topics"] if t in include]
        ready = max([1] + needed)
        if p["level"] == "L3":  # hard problems only after some L2 practice
            ready = max(ready, (weeks + 1) // 2 + 1)
        prob_week[p["id"]] = ready
    base_cap = max(1, round(budget * practice_share / 2.5))  # ~2.5h per problem incl. review
    cap = {w: base_cap if w <= learn_weeks else max(2, round(budget / 2.5)) for w in range(1, weeks + 1)}
    pweeks = {w: [] for w in range(1, weeks + 1)}
    file_order = {p["id"]: i for i, p in enumerate(problems)}
    queue = sorted(prob_week, key=lambda pid: (prob_week[pid], file_order[pid]))
    # greedy: each week takes the earliest-ready problems (easier levels first by file order)
    for w in range(1, weeks + 1):
        ready = [pid for pid in queue if prob_week[pid] <= w]
        lvl = lambda pid: LEVEL_ORDER.get(next(p["level"] for p in problems if p["id"] == pid), 2)
        ready.sort(key=lambda pid: (lvl(pid), file_order[pid]))
        if w > learn_weeks and max_level == 3:  # senior+: each practice week gets one hard problem
            hard = [pid for pid in ready if lvl(pid) == 3]
            if hard:
                ready.remove(hard[0])
                ready.insert(0, hard[0])
        for pid in ready[:cap[w]]:
            pweeks[w].append(pid)
            queue.remove(pid)
    if per_week_h > learn_budget * 1.25:
        needed = int(-(-total_h // learn_budget) / 0.8) + 1
        extra = ""
        if "depth" in tracks:
            extra = ", or drop the depth track (--goal interview with --level mid, or --skip-topics)"
        print(f"Heads-up: {len(todo)} topics (~{total_h:g} h of study) in {learn_weeks} learning weeks "
              f"needs about {per_week_h / (1 - practice_share):.0f} h/week including practice, "
              f"not {budget:g}. Options: --weeks {needed}, more hours per week, "
              f"--known for topics already mastered{extra}. The plan below is front-loaded "
              f"to fit the weeks you gave.")

    for w in range(1, weeks + 1):
        plan.append({"week": w, "topics": buckets[w], "problems": pweeks[w],
                     "mock": args.goal != "real-world" and w >= max(2, weeks - 1)})

    st = {
        "version": 1,
        "profile": {
            "name": args.name, "goal": args.goal, "level": args.level,
            "weeks": weeks, "hours_per_week": budget,
            "start": args.start or today().isoformat(),
            "target_date": args.target_date, "notes": args.notes,
        },
        "plan": plan,
        "topics": {t: {"status": "done" if t in known else "todo", "quiz": None,
                       "reviews": [], "next_review": None, "notes": ""} for t in order},
        "attempts": [],
        "log": [],
        "created": today().isoformat(),
    }
    save_state(args, st)
    unscheduled = [p for p in problems if p["id"] not in {x for v in pweeks.values() for x in v}
                   and LEVEL_ORDER.get(p["level"], 2) <= max_level]
    print(f"Plan created in {d}/ — {len(todo)} topics, "
          f"{sum(len(v) for v in pweeks.values())} problems over {weeks} weeks "
          f"(~{budget} h/week).")
    if unscheduled:
        print(f"{len(unscheduled)} more problems available as extra practice "
              f"(`progress.py problems --eligible`).")
    print(f"Readable plan: {d/'progress.md'}")


def _csv(s):
    return [x.strip() for x in (s or "").split(",") if x.strip()]


# ---------------------------------------------------------------- updates
def cmd_topic(args):
    st = load_state(args)
    _, catalog, _ = load_catalog()
    if args.id not in catalog:
        sys.exit(f"Unknown topic '{args.id}'. See `progress.py topics`.")
    t = st["topics"].setdefault(args.id, {"status": "todo", "quiz": None, "reviews": [],
                                          "next_review": None, "notes": ""})
    if args.status:
        t["status"] = args.status
        if args.status == "done" and not t.get("next_review"):
            t["next_review"] = (today() + dt.timedelta(days=REVIEW_INTERVALS[0])).isoformat()
            t["completed"] = today().isoformat()
    if args.quiz is not None:
        t["quiz"] = args.quiz
        if args.quiz < 3:  # didn't really get it yet -> keep learning, review soon
            t["status"] = "learning" if t["status"] == "done" else t["status"]
            t["next_review"] = (today() + dt.timedelta(days=1)).isoformat()
    if args.notes:
        t["notes"] = (t.get("notes", "") + "\n" + args.notes).strip()
    save_state(args, st)
    print(f"{args.id}: {t['status']}" + (f", quiz {t['quiz']}/4" if t["quiz"] is not None else "")
          + (f", next review {t['next_review']}" if t.get("next_review") else ""))


def cmd_review(args):
    st = load_state(args)
    t = st["topics"].get(args.id)
    if not t:
        sys.exit(f"Topic '{args.id}' is not in this plan.")
    t["reviews"].append({"date": today().isoformat(), "quiz": args.quiz})
    passed = args.quiz >= 3
    streak = 0
    for r in reversed(t["reviews"]):
        if r["quiz"] >= 3:
            streak += 1
        else:
            break
    if passed:
        idx = min(streak, len(REVIEW_INTERVALS) - 1)
        t["next_review"] = (today() + dt.timedelta(days=REVIEW_INTERVALS[idx])).isoformat()
        t["status"] = "done"
    else:
        t["next_review"] = (today() + dt.timedelta(days=1)).isoformat()
        t["status"] = "learning"
    save_state(args, st)
    print(f"{args.id}: review {'passed' if passed else 'missed'} — next review {t['next_review']}")


def cmd_grade(args):
    st = load_state(args)
    problems = {p["id"]: p for p in load_problems()}
    if args.problem not in problems:
        sys.exit(f"Unknown problem '{args.problem}'. See `progress.py problems`.")
    rubric = {}
    for part in _csv(args.rubric):
        k, _, v = part.partition("=")
        if k.strip() in RUBRIC_KEYS:
            rubric[k.strip()] = int(v)
    n = 1 + sum(1 for a in st["attempts"] if a["problem"] == args.problem)
    saved = None
    if args.submission:
        src = Path(args.submission)
        if src.exists():
            sub = state_dir(args) / "submissions"
            sub.mkdir(parents=True, exist_ok=True)
            saved = sub / f"{args.problem}-attempt{n}{src.suffix}"
            shutil.copy2(src, saved)
            saved = str(saved.relative_to(state_dir(args)))
        else:
            print(f"warning: submission file {src} not found; recording grade without it",
                  file=sys.stderr)
    attempt = {"problem": args.problem, "attempt": n, "date": today().isoformat(),
               "score": args.score, "passed": args.score >= PASS_SCORE, "rubric": rubric,
               "gaps": _csv(args.gaps), "submission": saved, "notes": args.notes or ""}
    st["attempts"].append(attempt)

    # schedule weak topics for review
    weak = set()
    for k, v in rubric.items():
        if v <= 2:
            weak |= set(RUBRIC_TOPICS.get(k, []))
            if k in ("arch", "deep"):
                weak |= set(problems[args.problem]["topics"])
    scheduled, not_learned = [], []
    for t in sorted(weak):
        info = st["topics"].get(t)
        if not info:
            continue
        if info["status"] in ("done", "learning"):
            info["next_review"] = (today() + dt.timedelta(days=1)).isoformat()
            scheduled.append(t)
        elif info["status"] == "todo":
            not_learned.append(t)
    save_state(args, st)
    verdict = "PASSED" if attempt["passed"] else f"not yet (pass = {PASS_SCORE})"
    print(f"{args.problem} attempt {n}: {args.score}/100 — {verdict}")
    if scheduled:
        print("Scheduled for review tomorrow: " + ", ".join(scheduled))
    if not_learned:
        print("Related topics not studied yet (worth doing before a resubmission): " + ", ".join(not_learned))


def cmd_log(args):
    st = load_state(args)
    st["log"].append({"date": today().isoformat(), "minutes": args.minutes, "note": args.note or ""})
    save_state(args, st)
    print(f"Logged {args.minutes} min. Streak: {streak_days(st)} day(s).")


# ---------------------------------------------------------------- views
def streak_days(st) -> int:
    days = {dt.date.fromisoformat(e["date"]) for e in st["log"]}
    days |= {dt.date.fromisoformat(a["date"]) for a in st["attempts"]}
    d, n = today(), 0
    if d not in days:
        d -= dt.timedelta(days=1)
    while d in days:
        n += 1
        d -= dt.timedelta(days=1)
    return n


def best_scores(st):
    best = {}
    for a in st["attempts"]:
        best[a["problem"]] = max(best.get(a["problem"], 0), a["score"])
    return best


def due_reviews(st):
    t0 = today().isoformat()
    return sorted([tid for tid, t in st["topics"].items()
                   if t.get("next_review") and t["next_review"] <= t0 and t["status"] != "skipped"],
                  key=lambda tid: st["topics"][tid]["next_review"])


def weak_dimensions(st):
    sums, counts = {}, {}
    for a in st["attempts"][-6:]:
        for k, v in a["rubric"].items():
            sums[k] = sums.get(k, 0) + v
            counts[k] = counts.get(k, 0) + 1
    avg = {k: sums[k] / counts[k] for k in sums}
    return sorted([(k, round(v, 1)) for k, v in avg.items() if v < 3], key=lambda x: x[1])


def next_actions(st, limit=5):
    acts = []
    for tid in due_reviews(st)[:3]:
        acts.append(("review", tid))
    wk = week_of(st)
    best = best_scores(st)
    for w in st["plan"]:
        if w["week"] > wk + 1:
            break
        for tid in w["topics"]:
            if st["topics"].get(tid, {}).get("status") in ("todo", "learning"):
                acts.append(("learn", tid))
        for pid in w["problems"]:
            if best.get(pid, -1) < PASS_SCORE:
                acts.append(("practice", pid))
    seen, out = set(), []
    for a in acts:
        if a not in seen:
            seen.add(a)
            out.append(a)
    if not out:  # ahead of schedule: pull from later weeks
        for w in st["plan"]:
            for tid in w["topics"]:
                if st["topics"].get(tid, {}).get("status") in ("todo", "learning"):
                    out.append(("learn", tid))
            for pid in w["problems"]:
                if best.get(pid, -1) < PASS_SCORE:
                    out.append(("practice", pid))
    return out[:limit]


def cmd_status(args):
    st = load_state(args)
    _, catalog, _ = load_catalog()
    problems = {p["id"]: p for p in load_problems()}
    tt = st["topics"]
    done = sum(1 for t in tt.values() if t["status"] == "done")
    active = sum(1 for t in tt.values() if t["status"] != "skipped")
    best = best_scores(st)
    planned = [p for w in st["plan"] for p in w["problems"]]
    passed = sum(1 for p in planned if best.get(p, -1) >= PASS_SCORE)
    wk = week_of(st)
    # only count weeks that have fully ended, so nobody is "behind" on day 2
    expected_topics = sum(len(w["topics"]) for w in st["plan"] if w["week"] < wk)
    done_scheduled = sum(1 for w in st["plan"] if w["week"] < wk for t in w["topics"]
                         if tt.get(t, {}).get("status") == "done")
    minutes = sum(e["minutes"] for e in st["log"])
    p = st["profile"]
    print(f"{p['name'] or 'Learner'} — goal: {p['goal']}, target level: {p['level']}")
    print(f"Week {min(wk, p['weeks'])}/{p['weeks']} · topics {done}/{active} · "
          f"problems passed {passed}/{len(planned)} · study time {minutes/60:.1f} h · "
          f"streak {streak_days(st)} d")
    behind = expected_topics - done_scheduled
    if behind > 0:
        print(f"Behind schedule by {behind} topic(s) from weeks before week {wk}.")
    if st["attempts"]:
        last = st["attempts"][-1]
        print(f"Last attempt: {problems.get(last['problem'], {}).get('title', last['problem'])} "
              f"→ {last['score']}/100 ({last['date']})")
    wd = weak_dimensions(st)
    if wd:
        print("Weak rubric areas (recent avg/4): " + ", ".join(f"{k} {v}" for k, v in wd))
    dr = due_reviews(st)
    if dr:
        print("Reviews due: " + ", ".join(dr))
    print("Next up:")
    for kind, ident in next_actions(st):
        label = catalog[ident]["title"] if kind != "practice" else problems.get(ident, {}).get("title", ident)
        print(f"  - {kind}: {ident} — {label}")


def cmd_next(args):
    st = load_state(args)
    _, catalog, _ = load_catalog()
    problems = {p["id"]: p for p in load_problems()}
    for kind, ident in next_actions(st, limit=args.n):
        label = catalog[ident]["title"] if kind != "practice" else problems.get(ident, {}).get("title", ident)
        print(f"{kind}\t{ident}\t{label}")


def cmd_topics(args):
    catalog, _, phases = load_catalog()
    st = None
    if (state_dir(args) / "progress.json").exists():
        st = json.loads((state_dir(args) / "progress.json").read_text())
    for t in catalog:
        s = st["topics"].get(t["id"], {}).get("status", "-") if st else ""
        print(f"{t['phase']}\t{t['id']:<24}\t{t['track']:<8}\t{s:<9}\t{t['title']}")


def cmd_problems(args):
    probs = load_problems()
    st = None
    if (state_dir(args) / "progress.json").exists():
        st = json.loads((state_dir(args) / "progress.json").read_text())
    best = best_scores(st) if st else {}
    for p in probs:
        if args.eligible and st:
            ok = all(st["topics"].get(t, {}).get("status") in ("done", None) or t not in st["topics"]
                     for t in p["topics"])
            if not ok:
                continue
        b = best.get(p["id"])
        mark = "" if b is None else (f"best {b}" + (" ✓" if b >= PASS_SCORE else ""))
        print(f"{p['level']}\t{p['id']:<26}\t{mark:<10}\t{p['title']}")


def cmd_report(args):
    st = load_state(args)
    save_state(args, st)
    print(state_dir(args) / "progress.md")


def render_report(st) -> str:
    _, catalog, phases = load_catalog()
    problems = {p["id"]: p for p in load_problems()}
    p = st["profile"]
    best = best_scores(st)
    icon = {"done": "✅", "learning": "🟡", "todo": "⬜", "skipped": "➖"}
    out = [f"# System design progress — {p['name'] or 'Learner'}", "",
           f"Goal **{p['goal']}** · target level **{p['level']}** · {p['weeks']} weeks × "
           f"{p['hours_per_week']} h · started {p['start']}"
           + (f" · target {p['target_date']}" if p.get("target_date") else ""),
           f"_Updated {st.get('updated', '')}_", ""]
    tt = st["topics"]
    done = sum(1 for t in tt.values() if t["status"] == "done")
    planned = [x for w in st["plan"] for x in w["problems"]]
    passed = sum(1 for x in planned if best.get(x, -1) >= PASS_SCORE)
    out += [f"**Topics** {done}/{len(tt)} · **Problems passed** {passed}/{len(planned)} · "
            f"**Study time** {sum(e['minutes'] for e in st['log'])/60:.1f} h", ""]
    dr = due_reviews(st)
    if dr:
        out += ["**Reviews due:** " + ", ".join(dr), ""]
    out += ["## Plan", ""]
    for w in st["plan"]:
        out.append(f"### Week {w['week']}" + (" · mock interview week" if w.get("mock") else ""))
        for t in w["topics"]:
            info = tt.get(t, {})
            q = f" (quiz {info['quiz']}/4)" if info.get("quiz") is not None else ""
            out.append(f"- {icon.get(info.get('status', 'todo'), '⬜')} `{t}` {catalog[t]['title']}{q}")
        for pid in w["problems"]:
            b = best.get(pid)
            mark = "✅" if b is not None and b >= PASS_SCORE else ("🟡" if b is not None else "⬜")
            out.append(f"- {mark} 🧩 **{problems.get(pid, {}).get('title', pid)}**"
                       + (f" — best {b}/100" if b is not None else ""))
        out.append("")
    if st["attempts"]:
        out += ["## Assignment history", "", "| Date | Problem | Try | Score | Weak areas | Diagram |",
                "|---|---|---|---|---|---|"]
        for a in st["attempts"]:
            weak = ", ".join(k for k, v in a["rubric"].items() if v <= 2) or "—"
            out.append(f"| {a['date']} | {a['problem']} | {a['attempt']} | {a['score']} "
                       f"{'✅' if a['passed'] else ''} | {weak} | {a.get('submission') or ''} |")
        out.append("")
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------- cli
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dir", help="state folder (default ./sd-mentor or $SD_MENTOR_DIR)")
    sp = ap.add_subparsers(dest="cmd", required=True)

    s = sp.add_parser("init", help="create a study plan")
    s.add_argument("--name", default="")
    s.add_argument("--goal", choices=["interview", "real-world", "both"], default="both")
    s.add_argument("--level", choices=["junior", "mid", "senior", "staff"], default="mid")
    s.add_argument("--weeks", type=int, default=8)
    s.add_argument("--hours-per-week", type=float, default=8)
    s.add_argument("--start", help="YYYY-MM-DD (default today)")
    s.add_argument("--target-date", help="interview date, if any")
    s.add_argument("--known", help="comma-separated topic ids already mastered")
    s.add_argument("--add-topics", help="extra topic ids to include")
    s.add_argument("--skip-topics", help="topic ids to leave out")
    s.add_argument("--include-optional", action="store_true", help="include optional track (LLD)")
    s.add_argument("--notes", default="")
    s.add_argument("--force", action="store_true")
    s.set_defaults(fn=cmd_init)

    s = sp.add_parser("status"); s.set_defaults(fn=cmd_status)
    s = sp.add_parser("next"); s.add_argument("-n", type=int, default=5); s.set_defaults(fn=cmd_next)

    s = sp.add_parser("topic", help="update a topic")
    s.add_argument("id")
    s.add_argument("--status", choices=["todo", "learning", "done", "skipped"])
    s.add_argument("--quiz", type=int, choices=range(0, 5), help="concept check score 0-4")
    s.add_argument("--notes")
    s.set_defaults(fn=cmd_topic)

    s = sp.add_parser("review", help="record a spaced review")
    s.add_argument("id"); s.add_argument("--quiz", type=int, choices=range(0, 5), required=True)
    s.set_defaults(fn=cmd_review)

    s = sp.add_parser("grade", help="record a graded assignment")
    s.add_argument("--problem", required=True)
    s.add_argument("--score", type=int, required=True)
    s.add_argument("--rubric", default="", help="req=3,est=2,api=3,arch=3,deep=2,tradeoff=2,rel=1,clarity=4")
    s.add_argument("--gaps", default="")
    s.add_argument("--submission", help="path to the diagram/photo that was graded")
    s.add_argument("--notes")
    s.set_defaults(fn=cmd_grade)

    s = sp.add_parser("log", help="log study time")
    s.add_argument("--minutes", type=int, required=True); s.add_argument("--note")
    s.set_defaults(fn=cmd_log)

    s = sp.add_parser("report"); s.set_defaults(fn=cmd_report)
    s = sp.add_parser("topics"); s.set_defaults(fn=cmd_topics)
    s = sp.add_parser("problems"); s.add_argument("--eligible", action="store_true"); s.set_defaults(fn=cmd_problems)

    args = ap.parse_args(argv)
    args.fn(args)


if __name__ == "__main__":
    main()
