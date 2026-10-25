# Study plans and teaching guide

## Choosing a plan shape

`progress.py init` builds the week-by-week plan from the learner's answers; these presets are the
defaults to suggest when they don't know what to pick.

| Situation | Weeks × hours | Flags |
|---|---|---|
| Interview in ≤ 3 weeks | 3 × 12–15 | `--goal interview --known <what they already know>` — skim P1–P3, spend most time on problems + mocks |
| Standard interview prep | 8 × 8 | `--goal both --level mid` (or senior) |
| Senior/staff, thorough | 10–12 × 8 | `--goal both --level senior` (adds depth track: consensus, clocks, batch, search, LLM systems) |
| Real-world architecture (no interview) | 12 × 5 | `--goal real-world` — fewer timed mocks, more engineering-blog case studies and papers |
| Total beginner (< 2 yrs backend) | 12 × 6 | `--goal both --level junior` — L1/L2 problems only |

If they have an interview date, pass `--target-date` and size `--weeks` to finish a week before it.
If they already know topics, ask a 2–3 question spot check per claimed topic before marking it
`--known`; people overestimate here, and skipped foundations show up later as weak deep dives.

## Weekly rhythm (suggest it, don't impose it)

- ~60–65% learning topics: read/watch one "Learn" resource → 4-question concept check → mark done.
- ~35% practice: one problem per ~2.5 h (45–60 min solo attempt + review + resubmission).
- Start each session with any **reviews due** (spaced repetition: 1, 3, 7, 21, 60 days).
- Final 1–2 weeks (interview goal): timed mock interviews, 45 min, interviewer-style.

## Teaching a topic

A good topic session is short and active:

1. **Hook (2–3 sentences)** — the real problem this solves ("Your single Postgres box hits 10K writes/s. Now what?").
2. **Core idea** — explain plainly, with one diagram (Mermaid or inline visual) and one concrete number.
3. **Trade-offs** — what it costs and when *not* to use it. This is what interviews probe.
4. **Where it shows up** — 2–3 problems from `problems.md` that use it.
5. **One resource** — the "Learn" item from `resources.md` for that topic (plus "Go deeper" if they want).
6. **Concept check** — 3–4 questions (start from the "Check" line in `resources.md`), learner answers in their own words before you give anything away. Score 0–4 and record it.

Match depth to the learner: a senior engineer doesn't need "what is a cache"; ask them where cache
invalidation went wrong in a system they've built instead.

## Assigning a practice problem

Give the learner exactly what an interviewer would — the **Prompt** line from `problems.md`
(functional scope + scale) — and nothing from Must-haves/Deep dives/Mistakes.

Then tell them what to submit:

> Spend 45–60 minutes. Submit (1) requirements + rough estimates, (2) API + data model,
> (3) a high-level diagram — any of: a photo of paper/whiteboard, a screenshot, an Excalidraw or
> draw.io export (`.excalidraw`/`.drawio` files are graded most precisely), or Mermaid — and
> (4) notes on your deep dives and trade-offs. Clear labels and arrows help me grade what you
> actually drew.

If they get stuck, give the **smallest** useful hint (a question, not an answer): "What happens
when a celebrity with 100M followers posts?" Record hints in the grade notes; heavy hinting caps
the Deep-dives and Trade-offs scores at 2.

## Mock interview mode

Play the interviewer for 45 minutes of wall-clock-free conversation:
1. Give only the one-line problem ("Design WhatsApp"). Let them ask clarifying questions; answer like an interviewer (sensible defaults, numbers if asked).
2. Let them drive. Interject only with interviewer probes: "What's the bottleneck?", "What happens if this box dies?", "Why that database?"
3. At the end, ask for their final diagram (photo/file) and grade with the rubric, adding a "how this would read to an interviewer" paragraph with a hire/lean-hire/no-hire signal at their target level.
