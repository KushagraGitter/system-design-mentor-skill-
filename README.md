# System Design Mentor — an agent skill

A personal system design tutor for Claude. It plans your study, teaches topic by topic with the
best curated resources, gives you practice problems, **grades your own design diagrams** (a phone
photo of your whiteboard, a screenshot, an Excalidraw/draw.io file, or Mermaid), and tracks your
progress with spaced repetition.

```
You:    I have a senior backend interview in 8 weeks, ~8 hours a week. Help me prep system design.
Claude: builds an 8-week plan → teaches week 1 topics → assigns "Design a URL shortener"
You:    [photo of your notebook diagram]
Claude: transcribes what you drew → traces the read/write/failure paths → scores it on an
        8-dimension rubric (64/100) → shows your diagram fixed, as Mermaid → logs the attempt
        and schedules weak topics for review
```

## What's inside

```
system-design-mentor/
├── SKILL.md                     workflow: plan → teach → practice → review → track
├── assets/topics.json           42 topics in 9 phases, with prerequisites and study-hour estimates
├── references/
│   ├── resources.md             best free + paid resources per topic (books, Hello Interview,
│   │                            ByteByteGo, DDIA 2e, papers, engineering blogs, YouTube)
│   ├── problems.md              27 practice problems (L1–L3) with private answer keys
│   ├── review-rubric.md         how designs are transcribed, traced and scored (pass = 70/100)
│   └── study-plans.md           plan presets, how to teach a topic, mock interview mode
└── scripts/
    ├── progress.py              plan + progress tracker (stdlib Python)
    └── parse_diagram.py         extracts boxes/arrows/labels from .excalidraw, .drawio, Mermaid
```

**Curriculum phases**: Foundations · Building blocks · Data storage & modeling · Distributed systems
theory · Async & streaming · Patterns for scale · Reliability, observability & security · Interview
craft · Modern systems (LLM serving/RAG, collaborative editing).

**Problems** range from URL shortener and rate limiter to news feed, chat, Ticketmaster, Uber, ad
click aggregation, and senior-level payment systems, Google Docs, Dynamo-style KV stores, stock
exchanges and ChatGPT-style LLM services.

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
*"review my design"* + attach a photo, *"how am I doing?"*.

## Progress tracking

Everything is stored in `sd-mentor/` in your working directory:

- `progress.json` — the source of truth (plan, topic status, quiz scores, review schedule, attempts)
- `progress.md` — a readable report regenerated on every update
- `submissions/` — a copy of each diagram that was graded (`news-feed-attempt2.jpg`, …)

In Claude Code, commit that folder to keep your history. In claude.ai (files don't persist between
chats), download `progress.json` at the end of a session and attach it at the start of the next.

You can also use the tracker directly:
```bash
python3 system-design-mentor/scripts/progress.py init --goal both --level senior --weeks 8 --hours-per-week 8
python3 system-design-mentor/scripts/progress.py status
python3 system-design-mentor/scripts/progress.py next
python3 system-design-mentor/scripts/progress.py problems --eligible
```

## How designs are graded

1. **Transcribe** exactly what you drew (components, flows, sync vs async, notes) and ask about anything unreadable — no credit for things not on the page, no penalty for things missed by the reviewer.
2. **Trace** the main write path, read path, the scale hot-spot and a failure walk through your boxes.
3. **Score** 8 weighted dimensions: requirements, estimation, API & data model, architecture completeness, deep dives, trade-offs, reliability, diagram clarity → /100. 70 passes.
4. **Feedback**: what works, gaps by impact, must-have checklist, your diagram redrawn with fixes highlighted, interviewer follow-ups, what to study next.

## Contributing

Add problems to `references/problems.md` (keep the `### id — Title`, `Level:`, `Topics:` lines —
the tracker parses them) and resources to `references/resources.md` under the matching topic id.

## License

MIT
