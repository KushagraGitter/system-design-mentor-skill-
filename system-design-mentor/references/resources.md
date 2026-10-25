# Resource library (topic-wise)

Curated October 2026. Free resources are listed first in each section; paid ones are marked 💲.
Topic headings use the same `id` as `assets/topics.json` and the progress tracker, so you can jump
straight from a topic in a learner's plan to its resources.

Book chapter references point to **DDIA** (Kleppmann & Riccomini, *Designing Data-Intensive
Applications*, 2nd ed., O'Reilly, March 2026 — chapter numbers below are from the 1st edition, so
match by chapter title if the learner has the 2nd), **Xu-1 / Xu-2** (Alex Xu, *System Design
Interview* vols 1 and 2), and **UDS** (Roberto Vitillo, *Understanding Distributed Systems*).

When recommending, pick **one "Learn" item and at most one "Go deeper" item** per session. A learner
drowning in links learns less than one who finishes a single good read. Before handing a link to a
learner, prefer resources from this file; if you need something newer, search the web and say so.

## Contents
- [Core library (use across topics)](#core-library)
- [P1 Foundations](#p1-foundations) · [P2 Building blocks](#p2-core-building-blocks) · [P3 Data](#p3-data-storage-and-modeling)
- [P4 Distributed theory](#p4-distributed-systems-theory) · [P5 Async & streaming](#p5-async-processing-and-streaming)
- [P6 Patterns](#p6-design-patterns-for-scale) · [P7 Reliability & security](#p7-reliability-observability-and-security)
- [P8 Interview craft](#p8-interview-craft) · [P9 Modern systems](#p9-modern-systems-ai-llm-and-real-time)
- [Practice platforms, mocks, diagram tools](#practice-platforms-mocks-and-diagram-tools)

---

## Core library

**Free, start here**
- System Design Primer (Donne Martin) — the classic free overview with Anki decks: https://github.com/donnemartin/system-design-primer
- Hello Interview — *System Design in a Hurry* (core concepts, key technologies, patterns, 30+ problem breakdowns): https://www.hellointerview.com/learn/system-design/in-a-hurry/introduction
- ByteByteGo *System Design 101* — visual one-page explainers: https://github.com/ByteByteGoHq/system-design-101
- Karan Pratap Singh — *System Design* free course/book: https://github.com/karanpratapsingh/system-design
- AlgoMaster *Awesome System Design Resources* (curated links by concept): https://github.com/ashishps1/awesome-system-design-resources
- Awesome Scalability (real-world engineering-blog index): https://github.com/binhnguyennus/awesome-scalability
- Awesome Distributed Systems (papers, courses): https://github.com/theanalyst/awesome-distributed-systems
- Martin Fowler / Unmesh Joshi — *Patterns of Distributed Systems*: https://martinfowler.com/articles/patterns-of-distributed-systems/
- Azure Architecture Center — *Cloud design patterns* (vendor-neutral in practice): https://learn.microsoft.com/en-us/azure/architecture/patterns/
- Amazon Builders' Library — how Amazon actually builds (timeouts, retries, shuffle sharding…): https://aws.amazon.com/builders-library/
- Google SRE books (free online): https://sre.google/books/
- MIT 6.5840 Distributed Systems (lectures, papers, Raft labs): https://pdos.csail.mit.edu/6.824/

**Books**
- 💲 *Designing Data-Intensive Applications*, 2nd ed. (Kleppmann & Riccomini, 2026) — the depth book: https://www.oreilly.com/library/view/designing-data-intensive/9781098119058/
- 💲 *System Design Interview* vols 1 & 2 (Alex Xu, Sahn Lam) — the interview book; also on https://bytebytego.com
- 💲 *Understanding Distributed Systems* (Roberto Vitillo) — short, readable bridge to DDIA: https://understandingdistributed.systems/
- 💲 *AI Engineering* (Chip Huyen, O'Reilly 2025) — for the P9 AI-systems track

**YouTube**
- Hello Interview (walkthroughs by ex-FAANG interviewers)
- Jordan has no life (deep, DDIA-flavoured problem walkthroughs)
- ByteByteGo (short animated concept explainers)
- Gaurav Sen (intuition-first concepts)
- Hussein Nasser (backend/networking/database internals)
- Arpit Bhayani (real-world deep dives; free beginner series at https://arpitbhayani.me/sys-design)

**Engineering blogs** (use for "how did X really do it" deep dives)
- High Scalability: http://highscalability.com/ · Netflix: https://netflixtechblog.com/ · Uber: https://www.uber.com/blog/engineering/
- Meta: https://engineering.fb.com/ · Cloudflare: https://blog.cloudflare.com/ · Discord: https://discord.com/category/engineering
- Slack: https://slack.engineering/ · Stripe: https://stripe.com/blog/engineering · Jepsen analyses: https://jepsen.io/analyses

**Newsletters**: ByteByteGo, The Pragmatic Engineer, System Design One (https://newsletter.systemdesign.one/), AlgoMaster (https://newsletter.ashishps.com/)

---

## P1 Foundations

### fundamentals
- Learn: Hello Interview — *Introduction* and *Delivery framework* pages (in-a-hurry section)
- Learn: Xu-1 ch. 1 "Scale from zero to millions of users" — the single best first chapter
- Go deeper: DDIA ch. 1 "Reliable, Scalable, and Maintainable Applications"
- Check: Name 3 functional and 3 non-functional requirements for Instagram. What does "scalable" mean in numbers? Why is every design a trade-off?

### estimation
- Learn: Hello Interview — *Numbers to Know*: https://www.hellointerview.com/learn/system-design/core-concepts/numbers-to-know
- Learn: Xu-1 ch. 2 "Back-of-the-envelope estimation"
- Reference: Interactive latency numbers by year: https://colin-scott.github.io/personal_website/research/interactive_latency.html
- Check: 100M DAU each posting 2 photos/day of 500 KB — daily storage? 5-year storage? Peak write QPS with 3x peak factor? When does one Postgres box stop being enough?

### networking
- Learn: Hello Interview — *Networking Essentials*: https://www.hellointerview.com/learn/system-design/core-concepts/networking-essentials
- Learn: System Design Primer — DNS, CDN, TCP/UDP, HTTP sections
- Watch: Hussein Nasser — HTTP/2 vs HTTP/3, TCP vs UDP videos
- Check: What happens when you type a URL? When is UDP right? Why do WebSockets need sticky routing or a pub/sub layer?

### api-design
- Learn: Hello Interview — *API Design*: https://www.hellointerview.com/learn/system-design/core-concepts/api-design
- Go deeper: Stripe API idempotency posts on https://stripe.com/blog/engineering ; Google API Design Guide (https://cloud.google.com/apis/design)
- Check: Cursor vs offset pagination trade-offs? How does an idempotency key make "charge card" safe to retry? REST vs gRPC for internal services?

## P2 Core building blocks

### scaling-basics
- Learn: Xu-1 ch. 1; System Design Primer — "Performance vs scalability", "Latency vs throughput"
- Check: Why must app servers be stateless to scale horizontally? Where does session state go?

### load-balancing
- Learn: System Design Primer — "Load balancer", "Reverse proxy"
- Learn: Hello Interview — *API Gateway* deep dive: https://www.hellointerview.com/learn/system-design/deep-dives/api-gateway
- Go deeper: Builders' Library — "Using load shedding to avoid overload"
- Check: L4 vs L7? Round-robin vs least-connections vs consistent hashing? What breaks if the LB itself fails?

### caching
- Learn: Hello Interview — *Caching*: https://www.hellointerview.com/learn/system-design/core-concepts/caching and *Redis* deep dive: https://www.hellointerview.com/learn/system-design/deep-dives/redis
- Go deeper: Meta paper "Scaling Memcache at Facebook" (NSDI '13); Builders' Library — "Caching challenges and strategies"
- Check: Cache-aside vs write-through vs write-behind? How do you prevent a thundering herd on a hot key expiry? How stale may your cache be, and who decides?

### cdn-blob
- Learn: Hello Interview — *Handling Large Blobs*: https://www.hellointerview.com/learn/system-design/patterns/large-blobs
- Go deeper: Xu-2 "S3-like object storage"
- Check: Why upload directly to S3 with a presigned URL instead of through your API? How do you resume a 5 GB upload? Push vs pull CDN?

### proxies-gateway
- Learn: System Design Primer — "Reverse proxy"; Azure patterns — Gateway Routing / Gateway Offloading / Ambassador
- Check: What belongs in the gateway (auth, rate limiting, TLS) and what does not (business logic)?

## P3 Data storage and modeling

### sql-vs-nosql
- Learn: System Design Primer — "Database" section; Hello Interview — *PostgreSQL*, *DynamoDB*, *Cassandra* deep dives (`/learn/system-design/deep-dives/postgres`, `/dynamodb`, `/cassandra`)
- Go deeper: DDIA ch. 2 "Data Models and Query Languages"
- Check: Defend Postgres for a ticketing system. Defend Cassandra for a chat message store. What access patterns drive each choice?

### data-modeling
- Learn: Hello Interview — *Data Modeling*: https://www.hellointerview.com/learn/system-design/core-concepts/data-modeling
- Go deeper: Alex DeBrie, *The DynamoDB Book* 💲 (single-table design)
- Check: Model followers for Twitter in SQL and in a wide-column store. When is denormalization worth the write cost?

### indexing
- Learn: Hello Interview — *Database Indexing*: https://www.hellointerview.com/learn/system-design/core-concepts/db-indexing
- Go deeper: DDIA ch. 3 "Storage and Retrieval" (B-trees vs LSM-trees — essential)
- Check: Why are LSM-trees write-friendly? What does a composite index on (user_id, created_at) let you do? Cost of an index on writes?

### transactions
- Learn: DDIA ch. 7 "Transactions" (read it; nothing better exists)
- Watch: Hussein Nasser — isolation levels, MVCC
- Check: Show a lost-update anomaly and fix it two ways (row lock; OCC with version column). What does Postgres "Repeatable Read" actually guarantee?

### replication
- Learn: DDIA ch. 5 "Replication"; UDS replication chapters
- Check: Read-your-writes with async replicas — how? Multi-leader conflict resolution options? What does quorum R + W > N buy you and what doesn't it?

### sharding
- Learn: Hello Interview — *Sharding*: https://www.hellointerview.com/learn/system-design/core-concepts/sharding ; DDIA ch. 6 "Partitioning"
- Check: Pick a shard key for orders, chat messages, and a leaderboard. How do you handle a celebrity hot key? Cross-shard queries?

### consistent-hashing
- Learn: Hello Interview — *Consistent Hashing*: https://www.hellointerview.com/learn/system-design/core-concepts/consistent-hashing ; Xu-1 ch. 5
- Go deeper: Amazon Dynamo paper (SOSP 2007): https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf
- Check: Why virtual nodes? How much data moves when a node joins with naive mod-N vs a ring?

### search-systems
- Learn: Hello Interview — *Elasticsearch* deep dive: https://www.hellointerview.com/learn/system-design/deep-dives/elasticsearch
- Practice: Hello Interview — *FB Post Search* breakdown; Xu-1 ch. 13 "Search autocomplete"
- Check: How does an inverted index answer a two-term query? How do you keep the search index in sync with the primary DB (CDC)?

## P4 Distributed systems theory

### cap-pacelc
- Learn: Hello Interview — *CAP Theorem*: https://www.hellointerview.com/learn/system-design/core-concepts/cap-theorem
- Go deeper: DDIA ch. 9 "Consistency and Consensus" (linearizability part); Jepsen consistency map: https://jepsen.io/consistency
- Check: Which parts of a ticket-booking system need strong consistency and which can be eventual? What does PACELC add to CAP?

### consensus
- Learn: Raft site + visualisation: https://raft.github.io/ (paper: https://raft.github.io/raft.pdf)
- Learn: Hello Interview — *ZooKeeper* deep dive: https://www.hellointerview.com/learn/system-design/deep-dives/zookeeper
- Go deeper: MIT 6.5840 Raft labs; DDIA ch. 9
- Check: Why does Raft need a majority? What is a fencing token and why do distributed locks need one?

### distributed-txn
- Learn: Hello Interview — *Multi-step Processes*: https://www.hellointerview.com/learn/system-design/patterns/multi-step-processes
- Learn: microservices.io — Saga and Transactional Outbox patterns: https://microservices.io/patterns/data/saga.html
- Check: 2PC failure modes? Design a saga for "book flight + hotel + charge card" with compensations. Why is "exactly-once" really "effectively-once"?

### time-ordering
- Learn: DDIA ch. 8 "The Trouble with Distributed Systems"; Xu-1 ch. 7 "Design a unique ID generator"
- Check: Why can't you trust wall-clock timestamps for ordering? Snowflake ID layout? Lamport vs vector clocks?

## P5 Async processing and streaming

### queues
- Learn: System Design Primer — "Asynchronism"; Xu-2 "Distributed message queue"
- Go deeper: Builders' Library — "Avoiding insurmountable queue backlogs"
- Check: At-most/at-least/exactly-once? Where do poison messages go? How does backpressure reach the producer?

### streaming
- Learn: Hello Interview — *Kafka* deep dive: https://www.hellointerview.com/learn/system-design/deep-dives/kafka and *Flink*: https://www.hellointerview.com/learn/system-design/deep-dives/flink
- Go deeper: DDIA ch. 11 "Stream Processing"; Jay Kreps, "The Log: What every software engineer should know…" (LinkedIn Engineering, 2013)
- Check: How do partitions give ordering and parallelism at once? What happens on consumer-group rebalance? Windowing for "clicks per ad per minute"?

### batch-processing
- Learn: DDIA ch. 10 "Batch Processing"; MapReduce paper (OSDI '04)
- Check: Lambda vs kappa architecture — when would you still choose batch?

### workflows
- Learn: Hello Interview — *Managing Long Running Tasks*: https://www.hellointerview.com/learn/system-design/patterns/long-running-tasks ; *Temporal* deep dive: https://www.hellointerview.com/learn/system-design/deep-dives/temporal
- Practice: Hello Interview — *Job Scheduler* breakdown
- Check: How do you guarantee a scheduled job runs once even if a worker dies mid-run? Heartbeats vs visibility timeouts?

## P6 Design patterns for scale

### scaling-reads
- Learn: Hello Interview — *Scaling Reads*: https://www.hellointerview.com/learn/system-design/patterns/scaling-reads
- Go deeper: Azure patterns — CQRS, Materialized View
### scaling-writes
- Learn: Hello Interview — *Scaling Writes*: https://www.hellointerview.com/learn/system-design/patterns/scaling-writes
### contention
- Learn: Hello Interview — *Dealing with Contention*: https://www.hellointerview.com/learn/system-design/patterns/dealing-with-contention
- Practice: Ticketmaster, Online Auction, Flash Sale breakdowns (Hello Interview); Xu-2 "Hotel reservation system"
### realtime
- Learn: Hello Interview — *Real-time Updates*: https://www.hellointerview.com/learn/system-design/patterns/realtime-updates
- Practice: WhatsApp and FB Live Comments breakdowns; Xu-1 ch. 12 "Chat system"
### fanout-feeds
- Learn: Xu-1 ch. 11 "News feed system"; Hello Interview — *FB News Feed* breakdown
- Go deeper: Twitter/X timeline architecture talks ("Timelines at Scale", QCon 2013) — search the title
### rate-limiting
- Learn: Xu-1 ch. 4; Hello Interview — *Distributed Rate Limiter* breakdown
- Go deeper: Cloudflare blog — "How we built rate limiting capable of scaling to millions of domains"
### geo-systems
- Learn: Xu-2 "Proximity service" and "Nearby friends"; Hello Interview — *Yelp* and *Uber* breakdowns
- Check for all P6: name the pattern, the bottleneck it removes, and the new failure mode it introduces.

## P7 Reliability, observability and security

### reliability
- Learn: Builders' Library — "Timeouts, retries, and backoff with jitter" and "Making retries safe with idempotent APIs"
- Go deeper: Azure patterns — Circuit Breaker, Bulkhead, Retry; Michael Nygard, *Release It!* 💲
### availability-dr
- Learn: Google SRE book — chapters "Service Level Objectives" and "Embracing Risk": https://sre.google/books/
- Check: Two 99.9% services in series = ? Active-active vs active-passive multi-region? RPO vs RTO?
### observability
- Learn: Google SRE book — "Monitoring Distributed Systems" (the four golden signals); OpenTelemetry docs: https://opentelemetry.io/docs/
- Practice: Hello Interview — *Metrics Monitoring* breakdown; Xu-2 "Metrics monitoring and alerting system"
### security
- Learn: OWASP Top 10: https://owasp.org/www-project-top-ten/ ; OAuth 2.0 simplified: https://www.oauth.com/
- Check: Session cookies vs JWTs trade-offs? Where are secrets stored? How do you isolate tenants in a shared DB?
### deployment
- Learn: Martin Fowler — "Microservices", "MonolithFirst", "BlueGreenDeployment" articles on martinfowler.com
- Check: When is a monolith the right answer? How do you run a zero-downtime schema migration (expand/contract)?

## P8 Interview craft

### interview-framework
- Learn: Hello Interview — *Delivery framework*: https://www.hellointerview.com/learn/system-design/in-a-hurry/delivery
- Learn: Xu-1 ch. 3 "A framework for system design interviews"
### tradeoff-communication
- Learn: Hello Interview — leveling guidance (what mid/senior/staff answers look like) on the in-a-hurry pages
- Practice: record yourself; mock interviews (see below)
### low-level-design
- Learn: AlgoMaster *Awesome Low-Level Design*: https://github.com/ashishps1/awesome-low-level-design
- Go deeper: *Head First Design Patterns* 💲

## P9 Modern systems: AI/LLM and real-time

### llm-systems
- Learn: Hello Interview — *ChatGPT* problem breakdown: https://www.hellointerview.com/learn/system-design/problem-breakdowns/chatgpt
- Learn: Chip Huyen, *AI Engineering* 💲 (chapters on RAG, inference optimisation, evaluation)
- Go deeper: vLLM paper "Efficient Memory Management for LLM Serving with PagedAttention" (SOSP 2023)
- Check: Why does streaming tokens change your API and LB choices? Where does a vector DB fit and when is plain Postgres + pgvector enough? How do you cache LLM responses safely?
### collab-editing
- Learn: Hello Interview — *Google Docs* breakdown: https://www.hellointerview.com/learn/system-design/problem-breakdowns/google-docs
- Go deeper: Martin Kleppmann's CRDT talks; https://crdt.tech/

---

## Practice platforms, mocks and diagram tools

- Hello Interview problem breakdowns (free reading, 💲 for some premium content and mocks): https://www.hellointerview.com/learn/system-design
- Codemia — LeetCode-style system design practice with AI feedback: https://codemia.io/
- 💲 Mock interviews: interviewing.io, Exponent (https://www.tryexponent.com/), Hello Interview mocks
- Diagram tools the learner can submit from: Excalidraw (https://excalidraw.com, export PNG or `.excalidraw` JSON), draw.io / diagrams.net (`.drawio` XML or PNG), Mermaid (https://mermaid.js.org, text — easiest to grade precisely), tldraw, Miro, or a phone photo of paper/whiteboard.
