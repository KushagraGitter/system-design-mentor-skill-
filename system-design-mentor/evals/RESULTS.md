# Eval results

Last run: 26 October 2026 · Claude Code 2.1.310 · one run per case (so treat single-case numbers as
noisy) · LLM judge: Sonnet, 3 votes per check.

## Grading accuracy

Five submissions with known flaws, each graded by a fresh Claude session that has the skill and
none of the author's context. The same prompts were also run without the skill as a baseline.

| Case | Input | Planted problem | Score given | Checks passed (skill) | Baseline |
|---|---|---|---|---|---|
| `photo-url-shortener-misses-cache-fallback` | whiteboard photo (glare, skew) | no cache-miss path, counter coordination unspecified, alias/expiry ignored | 40 | 7/7 | 5/7 |
| `photo-news-feed-celebrity-and-smudge` | notebook photo, one illegible label | fan-out on write for 100M-follower accounts | 50 | 6/6 | 3/6 |
| `excalidraw-chat-no-routing` | `.excalidraw` | no cross-server message routing, no offline delivery, single MySQL | 16 | 4/5 | 5/5 |
| `drawio-ticketmaster-strong` | `.drawio` (compressed) | none — a strong design that should pass | 82 | 4/4 | 1/4 |
| `mermaid-rate-limiter-local-counters` | Mermaid | per-server counters (limit × 120 servers) | 24 | 4/4 | 4/4 |

**Overall: 96% of checks pass with the skill vs 69% without (+27 points).**

What the checks cover: correct transcription of what's drawn, no invented components, the planted
flaws found, an illegible label asked about instead of guessed, an improved diagram built from the
learner's own components, and a score in the expected range.

The one miss: the chat design scored 16, below the expected 20–55. Messages can't reach a recipient
on a different server, so the design fails its core requirement and the rubric's anchors put it
under 50; 16 is defensible. The range is left unchanged so the miss stays visible.

The baseline's misses were mostly about scores: without the rubric it either gave no score or
used a /10 scale, and it failed the strong design. It finds obvious flaws well on its own.

### What testing changed in the skill

The first run found every planted flaw but missed the expected score range in all five cases.
Two causes, both fixed in `references/review-rubric.md`:

1. **Penalizing what wasn't submitted.** A bare diagram doesn't show requirements, estimates or an
   API, and scoring those 0–1 dragged a strong design to 52. Those dimensions are now marked "not
   submitted" and the score is re-normalized over what was submitted.
2. **Inventing must-haves.** The reviewer marked extra concerns as missing must-haves. The ✅/❌
   checklist now lists exactly the answer key; other concerns go under "Gaps that matter".

Calibration anchors were also added. Separately, the reviewer correctly pointed out that the first
"strong" Ticketmaster fixture skipped the problem's hardest part (a payment that confirms after the
seat hold expired). The fixture was strengthened rather than the test loosened.

### Limits

These are synthetic submissions written by the skill's author. The next step is 10–15 real
submissions with scores a human agrees with, run several times each to measure variance.

## Triggering

`trigger-queries.json`: 10 messages that should load the skill and 10 near-misses that shouldn't
(production incidents, writing an ADR, hiring rubrics, code review, diagrams of a real system).

| Description | Should trigger | Should not trigger |
|---|---|---|
| Original | 4/10 | 0/10 false positives |
| Current | **7/10** | **0/10** false positives |

The original description missed practice questions, mock interviews, "explain and quiz me" and
design reviews; Claude answered those itself. The three remaining misses all say "here's my
photo/file" with no file actually attached in the test, so Claude asks for the file first. That's
reasonable behavior, and the skill loads once a file arrives.

## Re-running

```bash
cd system-design-mentor
claude plugin eval . --scaffold --allow-tools Bash Write Edit --judge-model sonnet
```
Shell tools need the sandbox (`bubblewrap` and `socat` on Linux). A full run with the baseline
costs roughly $12–14.
