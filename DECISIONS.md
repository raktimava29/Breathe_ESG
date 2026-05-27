# Architectural decisions

## Django apps split: `tenants`, `ingestion`, `records`

**Decision:** Three apps instead of one monolith module.

**Why:** Ingestion (raw + batches) changes for different reasons than review workflow. Keeps migrations and mental models separate without introducing microservices.

## Service layer outside views

**Decision:** `backend/services/` holds parsers, normalization, anomalies, review.

**Why:** DRF views stay thin; business logic is testable without HTTP. Avoids “fat serializers” anti-pattern.

## Raw JSON preservation

**Decision:** `RawRecord.payload` is never updated post-insert.

**Why:** Audit and dispute resolution require original evidence. Normalization mistakes can be re-run later without losing source data (re-run not implemented in prototype).

## Anomaly flags as separate rows

**Decision:** `AnomalyFlag` table instead of only embedding reasons in `status`.

**Why:** Multiple explainable rules can fire; analysts need per-rule context. Status `FLAGGED` is derived, not hand-edited.

## Tenant via header + scoped manager

**Decision:** `X-Tenant-Slug` + `TenantScopedManager` auto-filter.

**Why:** Explicit and debuggable. Subdomain tenancy was skipped to reduce local dev friction.

**Risk:** Forgetting `.unscoped()` in cross-tenant admin or anomaly duplicate checks — we use `unscoped()` only where intentional.

## Rule-based anomalies only

**Decision:** Thresholds, missing fields, duplicate hash, MoM variance ratio.

**Why:** Explainable heuristics match enterprise analyst expectations. ML would be unverifiable for this assignment scope.

## Mock travel API

**Decision:** Hard-coded booking list in `TravelApiParser` with POST `/api/ingest/travel/sync/`.

**Why:** Simulates OAuth/API pull without external dependencies. Shape mirrors Concur export fields (booking_id, airports, trip_type).

## SQLite escape hatch

**Decision:** `USE_SQLITE=true` for local runs without Docker.

**Why:** Intern assignment environments may lack PostgreSQL running.

## No authentication

**Decision:** `AllowAny` + analyst name in request body.

**Why:** Prototype focus is data trust workflow, not IAM. Production would add SSO and tie `reviewed_by` to authenticated user.
