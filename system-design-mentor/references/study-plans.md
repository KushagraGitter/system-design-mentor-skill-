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
5. **Three resources** from `resources.md` for that topic — at least one video and one text, the third whichever is best (two videos is fine). Format + time on each, ordered as a path: start here → then → go deeper. Don't ask how they like to learn; the mix covers it.
6. **Concept check** — 3–4 questions (start from the "Check" line in `resources.md`), learner answers in their own words before you give anything away. Score 0–4 and record it.

Match depth to the learner: a senior engineer doesn't need "what is a cache"; ask them where cache
invalidation went wrong in a system they've built instead.

## Skim checks (for topics they may already know)

Offer a skim check whenever a topic looks familiar to the learner, they say "I know this", or
they're behind schedule. It replaces the lesson, not the learning:

1. Ask 3 questions that need understanding, not recall — a trade-off, a failure case, and a number. (Use the topic's "Check" line; make at least one question about *when not* to use the thing.)
2. 3+/4 on the combined answer → mark it done as skimmed: `progress.py topic <id> --status done --quiz <n> --skim`, give the 3 resources as optional reading, move on.
3. Below 3 → teach it normally, starting from the gap the answers revealed.

Skimmed topics still enter spaced review, so a lucky pass gets caught later.

## Keeping the plan realistic

`progress.py status` prints the measured pace once a week has passed and warns when the remaining
topics won't fit. When it does (or the learner says they're behind), offer one of these, in a
sentence each, and let them pick:
- **More weeks**: `progress.py replan --weeks <n>`
- **Fewer hours, honestly sized**: `progress.py replan --use-measured` (sizes weeks from logged time)
- **Trim scope**: skim checks on familiar topics, or `replan --skip-topics <ids>` for depth topics they don't need

`replan` rebuilds only the weeks from now on; finished topics, quiz scores, reviews and graded
attempts are kept. Passed problems aren't rescheduled; failed ones come back.

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

A mock runs on the real clock — pacing is half of what's being tested, and you have no sense of
time passing between messages without it.

1. **Start the timer** when you give the problem: `python3 scripts/mock.py start --problem <id> --minutes 45 --level <their level>`. Give only the one-line problem ("Design WhatsApp") and say they have 45 minutes and should send their diagram (photo, screenshot or file) whenever they want feedback on it.
2. **Every turn, run `mock.py check` first.** It reports elapsed time, the phase they *should* be in, and an interrupt cue when one is due. When they move on ("ok, API next"), record it with `mock.py phase <requirements|entities-api|high-level|deep-dives|wrap-up>`.
3. **Act like an interviewer.** Answer clarifying questions with sensible defaults and numbers. Otherwise stay quiet and let them drive, except when:
   - `check` says to interrupt for time — redirect them in one sentence, the way a real interviewer would.
   - it says to probe, or the design invites one. Probes by phase:
     - requirements: "What's the read/write ratio?" · "Which of these matters most if we can only have one?"
     - high-level: "Walk me through a write end to end." · "Where does this data live?"
     - deep dives: "What's the bottleneck at 10x?" · "This box dies — what happens?" · "Why that database over X?" · the problem's own Deep dives line from `problems.md`.
   Keep probes to one question. Don't teach during a mock; save corrections for the review.
4. **End** with `mock.py end` when time is up (or they finish). Ask for the final diagram, then grade it with `review-rubric.md` and include:
   - the phase-timing table from `mock.py end` and one line on pacing (where they lost time);
   - a short "how this reads to an interviewer" paragraph with a hire / lean hire / lean no hire / no hire signal at their target level, and the one change that would most move it.
5. Record the grade with `progress.py grade` and add `--notes "mock"`.
