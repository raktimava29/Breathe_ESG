# Tradeoffs

## What we optimized for

- **Traceability:** Every normalized row links to raw JSON, batch, and source.
- **Explainability:** Normalization notes, anomaly messages, audit log entries.
- **Maintainability:** Small modules, no plugin framework for parsers.

## What we intentionally did not build

| Omitted | Reason |
|---------|--------|
| Async job queue (Celery) | Batches are small; synchronous pipeline is enough for prototype |
| Re-normalization job | Would need versioning on `NormalizedEmissionRecord`; out of scope |
| Full emission factor library | Scope categorization only; no CO₂e calculation |
| Row-level RBAC | Analyst name string only |
| Subdomain multi-tenancy | Header is simpler for Render/Railway deploy |
| Schema registry / Avro | JSON payloads sufficient for demo |
| Idempotent S3 ingestion | File upload only |

## What would fail at scale

1. **Synchronous pipeline** — Large CSVs (100k+ rows) will block HTTP workers. Needs chunked processing and batch status polling.
2. **MoM variance query** — Per-row aggregate over prior dates is O(n) per insert; needs pre-aggregated monthly stats per site.
3. **Duplicate detection via payload hash** — Collisions unlikely but full-table scan on hash without partition by tenant/month will slow down.
4. **bulk_create without ON CONFLICT** — Re-uploading same file creates duplicate raw rows (by design for audit; dedup policy is business decision).
5. **TenantScopedManager** — Easy to leak data if a developer uses raw `Model.objects` without tenant filter in new code.
6. **In-memory travel mock** — Not representative of rate-limited paginated APIs.

## Consistency choices

- **FLAGS refresh on each ingest** — Old flags deleted on re-detection for same record id only; re-ingest creates new records.
- **APPROVED immutability** — Strict except lock; rejects from FLAGGED go to PENDING, not a REJECTED terminal state (simpler state machine).

## Frontend tradeoffs

- Minimal styling; no component library — faster to ship analyst tables.
- Full page reload on tenant change — crude but avoids stale scoped data.
