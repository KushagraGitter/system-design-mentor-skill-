# Practice problem bank

Each problem gives you what you need to **assign** it (the prompt and scale to hand the learner)
and to **grade** it (must-haves, expected deep dives, common mistakes). Never show the learner the
must-haves or mistakes before they submit — that's the answer key.

Format is parsed by `scripts/progress.py` — keep the `### id — Title` heading and the
`Level:` / `Topics:` lines intact when adding problems. Topic ids come from `assets/topics.json`.

Levels: **L1** warm-up (after Phase 2), **L2** core interview (after Phase 3–5), **L3** hard /
senior+ (after Phase 6+).

## Contents
L1: url-shortener · pastebin · rate-limiter · unique-id-generator · key-value-cache
L2: news-feed · chat-app · notification-system · web-crawler · file-sync · video-streaming ·
typeahead · proximity-search · ticketmaster · leaderboard · job-scheduler · metrics-monitoring ·
ad-click-aggregator · ride-hailing · instagram
L3: payment-system · google-docs · distributed-kv-store · stock-exchange · llm-chat-service ·
distributed-message-queue · flash-sale
AI track (`--ai-track`): rag-qa-service · llm-gateway · ai-code-review-bot · ai-agent-platform ·
llm-eval-platform

---

## L1 — warm-ups

### url-shortener — Design a URL shortener (Bitly)
Level: L1
Topics: estimation, api-design, data-modeling, caching
Prompt: Users create short links for long URLs (optional custom alias, optional expiry) and anyone visiting the short link is redirected. 100M new URLs/month, 100:1 read:write.
Must-haves: write API + redirect API (301 vs 302 reasoning); short-code generation strategy (counter+base62, pre-generated key pool, or hash with collision handling); KV/SQL store keyed by code; cache in front of reads; uniqueness guarantee for custom aliases.
Deep dives: code generation without collisions across many app servers; cache hit rate and eviction; analytics counting without slowing redirects (async).
Common mistakes: hashing the URL and truncating with no collision handling; single counter as a SPOF with no batching; ignoring expiry; synchronous click-count writes on the redirect path.
Reference: Hello Interview — Bitly; Xu-1 ch. 8

### pastebin — Design Pastebin
Level: L1
Topics: api-design, cdn-blob, data-modeling, caching
Prompt: Users paste text (up to 10 MB), get a link, optional expiry and visibility. 10M pastes/day.
Must-haves: metadata DB separate from content in object storage; presigned or streamed upload; CDN for reads; expiry cleanup job.
Deep dives: storing blobs vs DB rows; cleanup at scale; abuse/rate limiting.
Common mistakes: 10 MB blobs stored in the relational DB; no TTL strategy.
Reference: System Design Primer — Pastebin solution

### rate-limiter — Design a distributed rate limiter
Level: L1
Topics: rate-limiting, caching, proxies-gateway, consistent-hashing
Prompt: Limit API clients per user/IP/API key with configurable rules across a fleet of 100+ API servers. 1M requests/sec peak.
Must-haves: algorithm choice with trade-off (token bucket / sliding window log / sliding window counter); placement (gateway/middleware); shared counter store (Redis) with atomic ops (Lua/INCR+EXPIRE); response semantics (429, Retry-After, headers).
Deep dives: race conditions; Redis sharding for counters; fail-open vs fail-closed when Redis is down; local + global hybrid limits.
Common mistakes: in-memory counters per server (limits multiply by fleet size); non-atomic read-modify-write.
Reference: Xu-1 ch. 4; Hello Interview — Distributed Rate Limiter

### unique-id-generator — Design a distributed unique ID generator
Level: L1
Topics: time-ordering, scaling-basics, availability-dr
Prompt: Generate 64-bit, roughly time-sortable, unique IDs at 100K/sec across multiple data centers with no coordination on the hot path.
Must-haves: Snowflake-style layout (timestamp + datacenter/worker id + sequence) or justified alternative; worker-id assignment; clock-skew handling.
Deep dives: clock moving backwards; exhausting the sequence in one ms; ID-assignment via ZooKeeper/etcd.
Common mistakes: UUIDv4 when sortability was required; DB auto-increment as a global SPOF.
Reference: Xu-1 ch. 7

### key-value-cache — Design a distributed cache (like Memcached/Redis cluster)
Level: L1
Topics: caching, consistent-hashing, replication, sharding
Prompt: An in-memory cache service for many internal teams: get/set/delete with TTL, 1 TB total, sub-ms p99.
Must-haves: partitioning via consistent hashing; eviction policy (LRU/LFU) and TTL; client-side vs proxy routing; replication or accepted loss on node failure.
Deep dives: hot keys; adding nodes without a mass miss storm; cache stampede protection.
Common mistakes: mod-N hashing; claiming strong consistency without explaining how.
Reference: Hello Interview — Distributed Cache

## L2 — core interview problems

### news-feed — Design a news feed (Facebook/Twitter timeline)
Level: L2
Topics: fanout-feeds, caching, queues, sharding, data-modeling
Prompt: Users follow others, post, and see a reverse-chronological feed. 500M DAU, avg 200 follows, some accounts with 100M followers. Feed load p99 < 500 ms.
Must-haves: post service + storage; follow graph store; feed generation strategy with explicit fan-out-on-write vs read and a **hybrid for celebrities**; feed cache (per-user list of post IDs); async fan-out workers via queue; pagination (cursor).
Deep dives: celebrity problem; feed cache sizing; ranking hook; edits/deletes propagating.
Common mistakes: pure fan-out-on-write without handling celebrities; JOINs across the follow table at read time at this scale; storing full posts inside every feed.
Reference: Xu-1 ch. 11; Hello Interview — FB News Feed

### chat-app — Design a chat app (WhatsApp/Messenger)
Level: L2
Topics: realtime, queues, sharding, data-modeling, reliability
Prompt: 1:1 and group chat (≤ 100 members), online presence, delivery/read receipts, offline delivery, multi-device. 1B users, 100B messages/day.
Must-haves: persistent connections (WebSockets) via a connection/gateway tier; routing a message to the recipient's connected server (pub/sub or session registry); durable message store partitioned by conversation; offline inbox + push notification; message ordering per conversation; ACK flow for receipts.
Deep dives: what happens when a gateway server dies; ordering and dedup (client message IDs); group fan-out; presence at scale (heartbeats, lazy).
Common mistakes: HTTP polling as the main path; no mapping user→connection server; one global sequence for ordering.
Reference: Hello Interview — WhatsApp; Xu-1 ch. 12

### notification-system — Design a notification system
Level: L2
Topics: queues, reliability, rate-limiting, workflows
Prompt: Internal services send push, SMS and email to users with templates, preferences/opt-outs, scheduling and retry. 50M notifications/day, spikes 10x.
Must-haves: notification API; per-channel queues and workers; third-party provider integration with retries + DLQ; user preferences store; dedup/idempotency; rate limiting per user.
Deep dives: exactly-once illusions (dedup keys); provider outage failover; scheduled sends at scale.
Common mistakes: synchronous calls to APNs/Twilio from the API path; no dedup → duplicate texts on retry.
Reference: Xu-1 ch. 10; Hello Interview — Notification System

### web-crawler — Design a web crawler
Level: L2
Topics: queues, scaling-writes, cdn-blob, distributed-txn
Prompt: Crawl 1B pages/month for a search engine; politeness to hosts; avoid duplicates; refresh changed pages.
Must-haves: URL frontier with priority + per-host politeness queues; DNS cache; fetchers; content dedup (hash / simhash); URL-seen set (Bloom filter or DB); blob storage for pages; robots.txt.
Deep dives: politeness at scale; crawler traps; recovering a crashed fetcher's work.
Common mistakes: a single FIFO queue (hammers one host); no dedup.
Reference: Xu-1 ch. 9; Hello Interview — Web Crawler

### file-sync — Design Dropbox / Google Drive
Level: L2
Topics: cdn-blob, data-modeling, realtime, transactions
Prompt: Upload, download, sync files across devices, share with others, version history. Files up to 50 GB. 100M users.
Must-haves: chunking + per-chunk hashes; presigned direct-to-blob uploads; metadata DB (files, versions, chunks); sync notification to other devices (long-poll/WebSocket/SSE); resumable uploads; dedup by chunk hash.
Deep dives: conflict handling when two devices edit offline; delta sync; large-file resume.
Common mistakes: uploading through app servers; whole-file re-upload on change.
Reference: Hello Interview — Dropbox; Xu-1 ch. 15

### video-streaming — Design YouTube / Netflix
Level: L2
Topics: cdn-blob, queues, workflows, caching
Prompt: Creators upload videos; viewers stream on any device with adaptive quality. 1M uploads/day, 1B views/day.
Must-haves: resumable upload to blob storage; async transcoding pipeline (DAG of jobs) into multiple bitrates + segments (HLS/DASH); CDN delivery; metadata service; view counting async.
Deep dives: transcoding orchestration and retries; CDN cost/hot vs long-tail content; resumable upload.
Common mistakes: streaming from origin servers; synchronous transcoding in the upload request.
Reference: Hello Interview — YouTube; Xu-1 ch. 14

### typeahead — Design search autocomplete
Level: L2
Topics: search-systems, caching, batch-processing, indexing
Prompt: Show top 10 completions as the user types; 10B queries/day; suggestions reflect trends within an hour.
Must-haves: trie (or prefix → top-k map) served from memory; offline/stream aggregation of query logs; periodic rebuild/swap; caching at edge/browser; sharding by prefix.
Deep dives: top-k maintenance; freshness vs cost; filtering offensive terms.
Common mistakes: querying the main DB with LIKE 'prefix%' per keystroke.
Reference: Xu-1 ch. 13

### proximity-search — Design Yelp / nearby places
Level: L2
Topics: geo-systems, indexing, caching, scaling-reads
Prompt: Search businesses within a radius, filter by category, view details and reviews. 200M businesses, 100K search QPS.
Must-haves: geospatial index (geohash/quadtree/S2 or PostGIS/Elasticsearch geo) with justification; read replicas/caching for search; separate write path for business updates.
Deep dives: neighbouring-cell edge cases; dense vs sparse areas; ranking.
Common mistakes: scanning lat/long with two B-tree range filters and calling it done.
Reference: Xu-2 "Proximity service"; Hello Interview — Yelp

### ticketmaster — Design a ticket booking system (Ticketmaster)
Level: L2
Topics: contention, transactions, caching, rate-limiting, realtime
Prompt: Browse events, view seat map, reserve seats for 10 minutes, pay, confirm. Popular events: 10M users hitting at on-sale time for 50K seats. No double booking.
Must-haves: seat reservation with expiry (DB row lock/OCC or distributed lock with TTL); strong consistency for booking; payment via external provider with idempotency; virtual waiting queue for surges; event search separated (read-heavy, cached).
Deep dives: hold expiry; waiting room design; payment failure after hold (charge succeeds after the hold expired); showing live seat availability to millions of viewers.
Common mistakes: eventual consistency on seat inventory; distributed lock without TTL/fencing; no surge protection.
Reference: Hello Interview — Ticketmaster; Xu-2 "Hotel reservation system"

### leaderboard — Design a real-time gaming leaderboard
Level: L2
Topics: caching, sharding, scaling-writes, realtime
Prompt: Global and friends leaderboards for a game with 50M DAU; scores update constantly; show top 10 and a user's rank.
Must-haves: Redis sorted sets (or justified alternative); score update path; rank query; sharding plan beyond one node; persistence/rebuild.
Deep dives: rank of an arbitrary user when sharded; ties; monthly resets.
Common mistakes: ORDER BY score on SQL per request at this scale.
Reference: Xu-2 "Real-time gaming leaderboard"

### job-scheduler — Design a distributed job scheduler
Level: L2
Topics: workflows, queues, consensus, reliability
Prompt: Users schedule one-off and cron jobs; 10M jobs/day; jobs must run within 2 s of schedule, at least once, ideally once.
Must-haves: job definition store vs execution store; time-indexed lookup of due jobs; queue to workers; leases/visibility timeouts + heartbeats; retry policy; idempotency guidance for job authors.
Deep dives: avoiding double execution; scheduler HA without duplicate dispatch; hot minute (everyone schedules at 00:00).
Common mistakes: a single cron box; polling the whole table every second.
Reference: Hello Interview — Job Scheduler

### metrics-monitoring — Design a metrics monitoring and alerting system
Level: L2
Topics: streaming, observability, scaling-writes, sql-vs-nosql
Prompt: Collect metrics from 1M hosts every 10 s, query dashboards, alert on rules. Retain 1 year with downsampling.
Must-haves: collection (push/pull) with justification; ingestion buffer (Kafka); time-series DB; downsampling/rollups; alert evaluator; notification path.
Deep dives: cardinality explosion; write throughput; alert dedup/flapping.
Common mistakes: relational DB as TSDB without rollups; alerting directly from raw ingestion without buffering.
Reference: Xu-2 "Metrics monitoring"; Hello Interview — Metrics Monitoring

### ad-click-aggregator — Design an ad click aggregator
Level: L2
Topics: streaming, batch-processing, scaling-writes, distributed-txn
Prompt: Record ad clicks (10K/s avg, 100K/s peak), redirect users, and let advertisers query clicks per ad per minute with < 1 min freshness; billing-grade accuracy.
Must-haves: click capture + redirect; event log (Kafka); stream aggregation (Flink/Spark) with windows; OLAP store for queries; reconciliation batch job for accuracy; dedup of clicks.
Deep dives: late/out-of-order events and watermarks; exactly-once-ish counting; hot ads.
Common mistakes: incrementing counters in the primary DB per click; no reconciliation.
Reference: Hello Interview — Ad Click Aggregator; Xu-2 "Ad click event aggregation"

### ride-hailing — Design Uber
Level: L2
Topics: geo-systems, realtime, contention, streaming
Prompt: Riders request rides, nearby drivers are matched, both see live location; 10M rides/day, drivers send location every 4 s.
Must-haves: high-write location ingestion into an in-memory geo index (Redis GEO / geohash cells); matching service with driver lock to avoid double-assignment; WebSocket/push updates; trip state machine persisted durably.
Deep dives: location write volume; matching consistency; surge pricing hook.
Common mistakes: writing every location ping to the primary SQL DB; two riders matched to one driver.
Reference: Hello Interview — Uber; Xu-2 "Nearby friends"

### instagram — Design Instagram
Level: L2
Topics: cdn-blob, fanout-feeds, caching, sharding
Prompt: Upload photos/videos, follow users, feed, likes and comments. 500M DAU.
Must-haves: media upload to blob + CDN with thumbnails/variants; metadata store; feed generation (see news-feed); counters for likes (sharded/async).
Deep dives: hot posts' like counters; media processing pipeline; feed.
Common mistakes: serving media from app servers; synchronous like counting on one row.
Reference: Hello Interview — Instagram

## L3 — hard / senior+

### payment-system — Design a payment system
Level: L3
Topics: distributed-txn, transactions, reliability, security, workflows
Prompt: Merchants charge customers via external PSPs; ledger, refunds, payouts; never double charge or lose money; reconcile daily.
Must-haves: idempotency keys end to end; payment state machine; double-entry ledger (append-only); async PSP integration with retries and webhooks; reconciliation; outbox/saga for multi-step flows; PCI scope minimisation (tokenisation).
Deep dives: PSP timeout — did it charge?; exactly-once illusion; ledger consistency.
Common mistakes: updating balances in place without a ledger; retrying non-idempotent calls.
Reference: Xu-2 "Payment system", "Digital wallet"; Hello Interview — Payment System

### google-docs — Design Google Docs
Level: L3
Topics: collab-editing, realtime, time-ordering, data-modeling
Prompt: Real-time collaborative editing with cursors, comments, version history, offline edits; up to 100 concurrent editors per doc.
Must-haves: OT or CRDT with justification; document session server (or sharded by doc) holding authoritative state; WebSocket fan-out; operation log + snapshots; presence.
Deep dives: convergence; offline merge; scaling hot documents.
Common mistakes: last-write-wins on whole document; locking paragraphs.
Reference: Hello Interview — Google Docs

### distributed-kv-store — Design a distributed key-value store (Dynamo-style)
Level: L3
Topics: consistent-hashing, replication, cap-pacelc, consensus, time-ordering
Prompt: Highly available KV store, tunable consistency, petabyte scale, multi-DC.
Must-haves: partitioning (ring + vnodes); replication factor N with quorum R/W; conflict handling (vector clocks or LWW with stated risk); failure detection (gossip); hinted handoff; anti-entropy (Merkle trees); storage engine (LSM).
Deep dives: sloppy quorum trade-offs; read repair; rebalancing.
Common mistakes: claiming CA; no conflict story.
Reference: Xu-1 ch. 6; Dynamo paper

### stock-exchange — Design a stock exchange matching engine
Level: L3
Topics: contention, time-ordering, availability-dr, realtime
Prompt: Accept orders, match them with price-time priority, publish market data; microsecond-ish latency; deterministic replay.
Must-haves: sequencer; single-threaded in-memory order book per symbol; event-sourced log for replay/recovery; market data fan-out; hot standby.
Deep dives: determinism; failover without losing or reordering orders.
Common mistakes: a database transaction per match; multi-threaded locking over one book.
Reference: Xu-2 "Stock exchange"; Hello Interview — Robinhood (adjacent)

### llm-chat-service — Design a ChatGPT-like LLM chat service
Level: L3
Topics: llm-systems, realtime, queues, rate-limiting, caching
Prompt: Users chat with an LLM, responses stream token by token, conversations persist, optional document Q&A (RAG). 50M DAU, GPU capacity is the bottleneck.
Must-haves: streaming transport (SSE/WebSocket) through gateway; inference request queue/scheduler with batching across a GPU fleet; per-user/tier rate limits and quotas; conversation store; RAG pipeline (chunking, embeddings, vector index, retrieval) if in scope; graceful degradation under load.
Deep dives: KV-cache / prefix caching; fair scheduling between tiers; cost controls; safety filtering placement.
Common mistakes: treating inference like a cheap stateless REST call; no admission control when GPUs saturate.
Reference: Hello Interview — ChatGPT; topic llm-systems in resources.md

### distributed-message-queue — Design a distributed message queue (Kafka-like)
Level: L3
Topics: streaming, replication, consensus, sharding
Prompt: Durable, ordered-per-partition log with producers, consumer groups, retention, replication.
Must-haves: topic → partitions → segment files; leader/follower replication with ISR-style acks; offset management per consumer group; controller/metadata via consensus.
Deep dives: acks=all trade-offs; leader failover without data loss; consumer rebalancing.
Common mistakes: per-message deletes on consume; global ordering.
Reference: Xu-2 "Distributed message queue"; Hello Interview — Kafka deep dive

### flash-sale — Design a flash sale system
Level: L3
Topics: contention, rate-limiting, queues, caching
Prompt: 1M users try to buy 10K discounted items at exactly 12:00; no overselling; fair; site stays up.
Must-haves: pre-warmed static/CDN content; admission control/waiting room; atomic inventory decrement (Redis Lua or DB conditional update) with reservation + timeout; async order creation via queue; bot protection.
Deep dives: oversell prevention under retries; reconciliation between Redis stock and DB.
Common mistakes: SELECT then UPDATE inventory; no admission control.
Reference: Hello Interview — Flash Sale

## AI track

### rag-qa-service — Design a document Q&A assistant (RAG) for a company's internal docs
Level: L2
Topics: rag-systems, llm-systems, search-systems, security, queues
Prompt: Employees ask questions in natural language and get answers with citations from 50M internal documents (wikis, PDFs, tickets) that change constantly. 20K questions/minute at peak; answers must respect each user's document permissions; p95 time-to-first-token under 2 s.
Must-haves: ingestion pipeline (connectors → parse → chunk → embed) driven by change events/queue; vector index plus keyword index (hybrid retrieval) with reranking; permission filtering at retrieval time using ACL metadata on chunks (not after generation); prompt assembly with citations; streaming answers; re-embedding/backfill strategy when the embedding model changes.
Deep dives: freshness (deletes and ACL changes must take effect fast); chunking strategy; eval loop for answer quality; cost per query.
Common mistakes: filtering permissions after the LLM has seen restricted text; one giant re-index job instead of incremental updates; no citations, so answers can't be checked; no way to measure retrieval quality.
Reference: resources.md → rag-systems; Eugene Yan, LLM patterns

### llm-gateway — Design an LLM gateway for a company
Level: L2
Topics: llm-gateway, rate-limiting, caching, reliability, observability
Prompt: Every team calls several LLM providers through one internal gateway. It must enforce per-team token budgets, route to the cheapest model that meets a quality tier, fail over when a provider is down, and log usage for chargeback. 5K requests/s, many of them streaming.
Must-haves: unified API with streaming passthrough; auth + per-team keys; token-based quotas/rate limits (counted on input + output tokens, reconciled after the response); routing table by model tier; provider health checks + fallback (before first token only, or with clear client semantics); usage events to a queue → billing/analytics store; optional semantic cache with scope rules.
Deep dives: rate limiting when output tokens aren't known up front; failover mid-stream; cache safety (no cross-tenant hits, no caching of personal data); latency overhead budget.
Common mistakes: request-count limits only; synchronous usage logging on the hot path; a shared semantic cache across tenants.
Reference: resources.md → llm-gateway; LiteLLM proxy docs

### ai-code-review-bot — Design an AI code review bot for GitHub pull requests
Level: L2
Topics: llm-systems, queues, workflows, rag-systems, rate-limiting
Prompt: When a PR is opened or updated, the bot posts review comments within 5 minutes. 2,000 orgs, 50K PRs/day, monorepos up to 10 GB. It should understand repo conventions, not just the diff.
Must-haves: webhook intake → durable queue (ack fast, process async); dedup/coalescing of rapid pushes to the same PR; job workers with per-repo concurrency limits and per-org rate limits for the GitHub API; context building (diff + related files + repo-level index/memory of conventions); LLM calls with retries and budgets; idempotent comment posting (don't double-post on retry); feedback capture (resolved/dismissed comments) for evals.
Deep dives: building and refreshing a per-repo index cheaply; noise control and comment quality evals; GitHub API rate limits; large diffs that exceed context windows.
Common mistakes: doing the review inside the webhook request; re-indexing the whole repo per PR; re-posting all comments on every push.
Reference: resources.md → rag-systems, llm-evals

### ai-agent-platform — Design a platform that runs autonomous coding agents
Level: L3
Topics: agent-systems, workflows, security, llm-gateway, observability
Prompt: Users give an agent a task ("fix this failing test"); it runs for up to 2 hours in an isolated sandbox with a repo checkout, calls tools (shell, file edits, web), and opens a PR. 100K agent runs/day, 10K concurrent.
Must-haves: run orchestrator with durable state (checkpointed agent loop, resumable after worker crash); sandbox pool (microVMs/containers) with warm pools, resource limits and network egress policy; tool-call gateway enforcing permissions and blast-radius limits (which paths/commands/hosts) with audit log; LLM access through a gateway with per-run budgets; streaming of run events to the UI; artifact/log storage; human approval step for risky actions.
Deep dives: resuming after a crash mid-tool-call (idempotent tools, checkpoints); sandbox scheduling and cold-start cost; prompt-injection from tool output; cost control for runaway loops.
Common mistakes: running agent code on shared hosts; keeping the agent loop only in a process's memory; giving tools ambient credentials.
Reference: resources.md → agent-systems

### llm-eval-platform — Design an LLM evaluation and tracing platform
Level: L3
Topics: llm-evals, streaming, batch-processing, observability, sql-vs-nosql
Prompt: Product teams log every LLM call and agent step (prompts, outputs, tool calls, latency, cost), browse traces, and run eval suites (datasets + scorers, including LLM-as-judge) on every prompt change. 500M spans/day; trace search within seconds; eval runs of 10K examples finish in under 15 minutes.
Must-haves: SDK/OTel-compatible ingestion → buffer (Kafka) → columnar/trace store with retention tiers; large payloads in object storage with pointers; trace query API (by session, user, tag, score); eval runner as a distributed batch job with concurrency limits against LLM providers; scorer framework (code checks, LLM judges) with versioned datasets and prompts; results comparison between runs; PII redaction and access control.
Deep dives: storage cost and sampling; judge reliability (calibrate against human labels); joining online traces to offline evals; multi-tenant isolation.
Common mistakes: storing full prompt/response blobs in the primary DB; running evals serially; no versioning, so results can't be compared.
Reference: resources.md → llm-evals

