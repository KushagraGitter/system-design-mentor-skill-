---
type: llm
focus: trace
weight: 1
---

The response identifies that reads go to Redis with no fallback path to Postgres on a cache miss (or that the read path to the database is missing).
