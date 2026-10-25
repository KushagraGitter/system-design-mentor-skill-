# System Design Mentor — an agent skill

A personal system design tutor for Claude. It plans your study, teaches topic by topic with
curated resources, gives you practice problems, **grades your own design diagrams** (a phone photo
of your whiteboard, a screenshot, an Excalidraw/draw.io file, or Mermaid), runs timed mock
interviews, and keeps your progress in a logbook that carries over between chats.

```
You:    I have a senior backend interview in 8 weeks, ~8 hours a week. Help me prep system design.
Claude: builds a plan (and warns if 8 h/week won't cover it) → creates your logbook →
        teaches week 1 topics with a video + reading path for each → assigns "Design a URL shortener"
You:    [photo of your notebook diagram]
Claude: transcribes what you drew (and asks about the label it can't read) → traces the read,
        write and failure paths → scores it on an 8-dimension rubric (58/100) → redraws your
        diagram with the fixes → shows a reference design side by side → logs the attempt and
        schedules your weak areas for review
```

## What it does

| | |
|---|---|
| **Plans** | Week-by-week plan from your goal, level, hours and interview date. Warns when the plan doesn't fit your time, measures your real pace, and `replan`s without losing history. **Skim checks** let you test out of topics you already know. |
| **Teaches** | 46 topics in 10 phases. Every topic has 3+ resources mixing video and text (Hello Interview, ByteByteGo, Gaurav Sen, Hussein Nasser, DDIA 2e, Alex Xu, papers, engineering blogs), plus concept checks and spaced review (1 → 3 → 7 → 21 → 60 days). |
| **Practice** | 32 problems from URL shortener to payment systems, stock exchanges and agent platforms, each with a private answer key and a **reference design** (Mermaid, plus a walkthrough video where one exists). |
| **Reviews your diagram** | Reads photos and screenshots directly and parses `.excalidraw`, `.drawio` and Mermaid exactly. Transcribes before judging, traces requests through your boxes, scores against a rubric (70 = pass), and redraws your design with the fixes. |
| **Mock interviews** | A real-clock timer: the interviewer knows when you've spent 10 minutes on requirements and cuts in like a real one would. Ends with a phase-timing table and a hire / no-hire signal for your target level. |
| **AI systems track** | Optional: RAG pipelines, LLM gateways, agent platforms and LLM evals, with 5 matching problems (`--ai-track`). |
| **Logbook** | In the Claude app, your plan, streak, scores, weak areas and attempts live in a private page in your artifacts, so every new chat picks up where you left off. |

## What's inside

```
system-design-mentor/
├── SKILL.md                         workflow: plan → teach → practice → review → track
├── assets/
│   ├── topics.json                  46 topics, 10 phases, prerequisites, study hours, tracks
│   └── dashboard.html               the logbook page
├── references/
│   ├── resources.md                 3+ resources per topic (video + text), with concept checks
│   ├── problems.md                  32 problems (L1–L3 + AI track) with private answer keys
│   ├── reference-designs.md         a reference design per problem, shown after grading
│   ├── review-rubric.md             how designs are transcribed, traced and scored
│   └── study-plans.md               plan presets, teaching, skim checks, pacing, mock mode
├── scripts/
│   ├── progress.py                  plan + progress tracker (init, replan, grade, status, dashboard…)
│   ├── parse_diagram.py             boxes/arrows/labels from .excalidraw, .drawio, Mermaid
│   ├── mock.py                      real-clock mock interview timer
│   └── check_links.py               finds broken resource links
└── evals/                           grading test cases (see "How accurate is the grading?")
```

## Install

**Claude Code** (personal skill):
```bash
git clone https://github.com/KushagraGitter/system-design-mentor-skill-.git
mkdir -p ~/.claude/skills && cp -r system-design-mentor-skill-/system-design-mentor ~/.claude/skills/
```
Or per project: copy the folder into `.claude/skills/` in your repo.

**Claude.ai / Claude app**: zip the `system-design-mentor` folder and upload it under
Settings → Capabilities → Skills (or ask Claude to package it as a `.skill` file).

Then just talk to Claude: *"help me learn system design"*, *"give me a design problem"*,
*"review my design"* + attach a photo, *"let's do a mock interview"*, *"how am I doing?"*.

## Where progress is kept

The scripts work on a local `sd-mentor/` folder (`progress.json`, a readable `progress.md`, and a
copy of every graded diagram in `submissions/`). Between chats it's kept in the best place available:

- **Claude app**: your **System Design Logbook** artifact — a private page that shows the plan and
  stores the full state. A new chat finds it and restores your progress automatically.
- **Claude Code**: commit `sd-mentor/` to a repo.
- **Neither**: Claude sends you `progress.json`; attach it next time.

The tracker also works on its own:
```bash
python3 system-design-mentor/scripts/progress.py init --goal both --level senior --weeks 8 --hours-per-week 8 --ai-track
python3 system-design-mentor/scripts/progress.py status
python3 system-design-mentor/scripts/progress.py replan --weeks 12
python3 system-design-mentor/scripts/mock.py start --problem news-feed
```

## How designs are graded

1. **Transcribe** exactly what you drew (components, flows, sync vs async, notes) and ask about anything unreadable — no credit for things not on the page, no penalty for things the reviewer missed.
2. **Trace** the main write path, read path, the scale hot-spot and a failure walk through your boxes.
3. **Score** 8 weighted dimensions: requirements, estimation, API & data model, architecture completeness, deep dives, trade-offs, reliability, diagram clarity → /100. 70 passes.
4. **Feedback**: what works, gaps by impact, must-have checklist, your diagram redrawn with fixes, interviewer follow-ups, what to study next, then a reference design to compare.

## How accurate is the grading?

`evals/` holds grading test cases with known answers, in every input format: two photo-like
hand-drawn submissions (whiteboard glare, a skewed notebook page, one deliberately illegible label),
an Excalidraw file, a draw.io file and a Mermaid answer. Each has planted flaws (or none — one is a
strong design that should pass) and checks for correct transcription, the specific gaps found, no
invented components, and a score in the right range.

Run them with Claude Code:
```bash
cd system-design-mentor && claude plugin eval . --scaffold --allow-tools Bash Write Edit
```

Latest results are in [`evals/RESULTS.md`](system-design-mentor/evals/RESULTS.md). These are
synthetic cases; real submissions with human-agreed scores are the next step — contributions welcome.

## Maintenance

A weekly GitHub Action (`.github/workflows/check-links.yml`) checks every resource link (YouTube
videos through oEmbed, so removed videos are caught) and opens an issue when something breaks.

To add a problem, add it to `references/problems.md` (keep the `### id — Title`, `Level:` and
`Topics:` lines — the tracker parses them) and its reference to `references/reference-designs.md`.
Add resources under the matching topic id in `references/resources.md`.

## License

MIT
