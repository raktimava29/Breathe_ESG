# Data model

## Design intent

The schema separates **immutable source evidence** from **interpreted canonical rows** and **analyst workflow state**. Every normalized row must trace to exactly one `RawRecord`, one `IngestionBatch`, and one `DataSource` under a `Tenant`.

## Entities

### Tenant
Company boundary. All tenant-owned tables include `tenant_id` FK. API resolves tenant via `X-Tenant-Slug` and scopes querysets in `TenantScopedManager`.

### DataSource
Per-tenant configuration for an upstream category: `SAP`, `UTILITY`, `TRAVEL`. One active source per category per tenant (unique constraint).

### IngestionBatch
Metadata for a single upload or API sync: filename, uploader, status, counts, errors. Does not store row payloads (those live in `RawRecord`).

### RawRecord
**Source of truth.** JSON `payload` as received/parsed; `payload_hash` for duplicate detection; never updated after insert.

### NormalizedEmissionRecord
Canonical analyst-facing row:
- GHG **scope** and **activity_category**
- Dates (activity + optional billing period for utilities)
- Quantities in source and **canonical** units
- `source_fields` copy for UI comparison
- `normalization_notes` for explainability
- **Review status** with immutability rules on `save()`

### AnomalyFlag
Rule hits decoupled from status. Multiple flags per record; drives `FLAGGED` when present.

### ReviewDecision
Explicit analyst transitions (approve / reject / lock).

### AuditLog
Append-only events for batches and records (action, actor, before/after JSON).

### UnitConversionMap
Global reference data (not tenant-scoped). Maps messy units (GAL, MWh) to canonical units.

## Relationships

```
Tenant
  ├── DataSource (1:N, unique per category)
  ├── IngestionBatch (N)
  │     └── RawRecord (N)
  │           └── NormalizedEmissionRecord (1:1)
  │                 ├── AnomalyFlag (N)
  │                 └── ReviewDecision (N)
  └── AuditLog (N)
```

## Status machine

| Status   | Meaning                          |
|----------|----------------------------------|
| PENDING  | Awaiting review                  |
| FLAGGED  | Anomaly rules fired              |
| APPROVED | Analyst signed off               |
| LOCKED   | Immutable for audit              |

Transitions enforced in `services/review/workflow.py`. `LOCKED` blocks all edits; `APPROVED` only allows transition to `LOCKED`.

## Traceability checklist

For any `NormalizedEmissionRecord` id:
1. `raw_record_id` → full upstream payload
2. `batch_id` → upload time, filename, uploader
3. `data_source_id` → SAP / UTILITY / TRAVEL
4. `tenant_id` → company isolation
5. `AuditLog` filtered by `entity_type` + `entity_id`
