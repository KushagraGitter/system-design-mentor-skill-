# Reviewing a submitted design

The learner's own diagram is the thing being graded. The most common failure when reviewing is
grading the design you *expected* instead of the one they *drew* — giving credit for a cache that
isn't there, or criticising a missing queue that is sitting in the corner of the photo. The
procedure below exists to prevent that: transcribe first, confirm, then grade.

## 1. Ingest the submission

| What they send | How to read it |
|---|---|
| Photo of paper / whiteboard, screenshot, PNG/JPG/PDF export | Open it with your image/file viewer (in Claude Code: the `Read` tool on the file path). Look at the whole image, then zoom into regions mentally: boxes, arrows, labels, side notes. |
| `.excalidraw` (JSON) | `python3 scripts/parse_diagram.py <file>` → components, labelled arrows, free text. If they also have a PNG, look at both: the JSON gives exact labels, the image gives layout and grouping. |
| `.drawio` / diagrams.net XML (also compressed) | `python3 scripts/parse_diagram.py <file>` |
| Mermaid (`.mmd`, or a ```mermaid block) / PlantUML / plain-text description | Read directly; `parse_diagram.py` handles Mermaid flowcharts too. |
| A link (Excalidraw share link, Miro, Figma, Google Drawings) | Usually not readable without auth. Ask for an exported PNG or the `.excalidraw`/`.drawio` file. |

If a photo is too blurry, cropped, or the handwriting on a label is ambiguous, **say exactly which
parts you can't read** ("the box between the LB and the DB — 'Cache' or 'Queue'?") and ask, rather
than guessing. A wrong guess turns into a wrong grade.

## 2. Transcribe before you judge

Write back a short, neutral transcription so the learner can correct you:

```
What I see in your diagram
Components: Client (mobile/web) · API Gateway · URL Service ×N · Redis cache · Postgres (primary + 2 replicas) · Key Generation Service · Kafka · Analytics worker · ClickHouse
Flows:
  1. Client → Gateway → URL Service → Postgres (create short URL)            [labelled "POST /urls"]
  2. Client → Gateway → URL Service → Redis → (miss) Postgres replica        [labelled "GET /{code}"]
  3. URL Service → Kafka → Analytics worker → ClickHouse                       [dashed = async]
Notes on the side: "base62, 7 chars", "TTL 24h", "~1.2K writes/s, 120K reads/s"
Unclear: arrow from Key Generation Service — does it go to URL Service or straight to Postgres?
```

Keep inferences out of the transcription. "Dashed arrow labelled async" is a transcription;
"they understand eventual consistency" is not. If the learner is waiting and the transcription has
no unclear items, you can proceed straight to grading in the same reply.

Also note what kind of diagram it is — a high-level component diagram, a sequence diagram, a data
model/ERD — and grade it for what it is trying to show.

## 3. Trace it

Walk real requests through *their* boxes and arrows. This is where real gaps surface.

1. **Main write path** — e.g. "create post": every hop, what is persisted where, what is sync vs async.
2. **Main read path** — e.g. "load feed": where does each piece of data come from, what's cached.
3. **Scale check** — take their (or the problem's) numbers: which box gets the most QPS / storage? Is it partitioned or replicated? Does any single box need to do more than it plausibly can?
4. **Failure walk** — kill one thing at a time: an app server, the cache, the DB primary, the queue, a region. What happens to users and to data?
5. **The problem's hard part** — every problem in `problems.md` has a "Deep dives" line. Did they address it (on the diagram or in notes)?

## 4. Score with the rubric

Score each dimension 0–4 against what is on the diagram plus whatever they wrote or said alongside it.
Weighted total is out of 100.

| # | Dimension | Weight | 0 | 2 | 4 |
|---|---|---|---|---|---|
| 1 | Requirements & scope | 10 | none stated | functional reqs only | functional + NFRs (latency, availability, consistency) with explicit scope cuts |
| 2 | Estimation | 10 | none | rough QPS or storage | QPS, storage, bandwidth, and they *use* the numbers to make a decision |
| 3 | API & data model | 15 | missing | endpoints or schema, not both | clear APIs (incl. pagination/idempotency where it matters) + entities with keys/indexes matched to access patterns |
| 4 | Architecture completeness | 20 | core path missing | core path works, some must-haves missing | every must-have from `problems.md` present and wired correctly |
| 5 | Deep dives & bottlenecks | 15 | none | names the bottleneck | resolves the problem's hard part concretely (algorithms, data structures, numbers) |
| 6 | Trade-offs & justification | 15 | technology chosen with no reason | some reasons | alternatives named and rejected for stated reasons tied to requirements |
| 7 | Reliability & failure handling | 10 | single points of failure ignored | replication/retries mentioned | failure walk handled: redundancy, retries+idempotency, degradation, data safety |
| 8 | Diagram clarity | 5 | can't follow | readable with effort | labelled boxes, directional arrows, sync/async distinguished, data stores obvious |

Weighted score = Σ (score/4 × weight).

**Bands**: < 50 *Not yet* · 50–69 *Developing* · 70–84 *Interview-ready (mid-level)* · 85+ *Strong
(senior signal)*. An assignment is **passed at 70+** — this threshold drives the progress tracker.

Level expectations (adjust when the learner told you their target level): mid-level candidates
need a correct, complete high-level design; senior candidates must also drive deep dives and
trade-offs unprompted; staff candidates should reframe requirements and reason about evolution,
cost, and org/operational concerns.

Be calibrated. A design that would fail a real interview should not score 80 because the learner
worked hard. Equally, don't dock points for a valid choice that differs from the reference answer
(Cassandra instead of DynamoDB, SSE instead of WebSockets) — dock only for choices that don't
meet the requirements or aren't justified.

## 5. Write the feedback

Use this structure. Lead with the score so the learner sees the verdict, keep it scannable.

```
## Review: <problem title> — <score>/100 (<band>)  ·  attempt <n>

**What works** (2–4 bullets, specific: "Splitting metadata from blob storage and using presigned uploads keeps app servers out of the 50 GB path")

**Gaps that matter** (ordered by impact; each = what's wrong → why it breaks → how to fix)
1. …
2. …

**Must-have checklist**: ✅ chunking · ✅ presigned upload · ❌ sync notification to other devices · ⚠️ dedup (mentioned, not shown)

**Rubric**: Req 3/4 · Est 2/4 · API/Data 3/4 · Arch 3/4 · Deep 2/4 · Trade-offs 2/4 · Reliability 1/4 · Clarity 4/4

**Improved design** (a Mermaid diagram of *their* design with the fixes applied — keep their component names so they can see the delta)

**Your follow-up** (1–2 interviewer-style questions to answer next, e.g. "Two devices edit the same file offline — walk me through what happens.")

**Study next**: <topic id(s)> — <one specific resource from resources.md>
```

The "Improved design" should be an edit of their diagram, not a fresh reference architecture. The
learner learns from seeing their own boxes rearranged; a polished stranger's diagram teaches much
less. Mark new or changed parts (e.g. a `classDef new fill:#d4f7d4` in Mermaid).

## 6. Record it

After the review, log it (see SKILL.md → Progress tracking):

```
python3 scripts/progress.py grade --problem <id> --score <0-100> \
  --rubric "req=3,est=2,api=3,arch=3,deep=2,tradeoff=2,rel=1,clarity=4" \
  --gaps "sync notification,failure handling" --submission <path-to-diagram>
```

Topics tied to low-scoring dimensions get scheduled for review automatically. Encourage a
resubmission for anything under 70 — redrawing after feedback is where most of the learning happens.

## Validating "explain it" answers (no diagram)

For concept checks ("explain consistent hashing"), score on: correct core idea (0–2), a concrete
example or numbers (0–1), the trade-off/limitation (0–1). 3+/4 = topic quiz passed. Ask them to
explain in their own words first; correct misconceptions directly and say what was right.
