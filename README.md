# Breathe ESG — Enterprise ingestion prototype

Multi-tenant ESG data ingestion and analyst review workflow. Ingests messy SAP, utility, and travel data; preserves raw records; normalizes to a canonical schema; flags anomalies; supports approve/lock audit flow.

## Stack

- **Backend:** Django 5 + Django REST Framework
- **DB:** PostgreSQL (SQLite for quick local dev)
- **Frontend:** React (Vite)
- **Deploy:** Docker Compose, `render.yaml` stub

## Quick start (SQLite, no Docker)

```powershell
cd "c:\Users\rakti\Desktop\Web Dev\Breathe_ESG"
pip install -r requirements.txt
$env:USE_SQLITE="true"
$env:PYTHONPATH="backend"
cd backend
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

In another terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 — tenant defaults to `acme-corp`.

Upload sample CSVs from `sample_data/` or use **Sync travel bookings**.

## Quick start (PostgreSQL)

```powershell
docker compose up --build
```

API: http://localhost:8000/api/

## Deploy on Render (single web service, no Blueprint)

1. Create **PostgreSQL** on Render → copy **Internal Database URL**.
2. Create **Web Service** (Python) from your GitHub repo.

**Build command:**

```bash
pip install -r requirements.txt && cd frontend && npm ci && npm run build && cd ../backend && python manage.py collectstatic --noinput
```

**Start command:**

```bash
bash scripts/render_start.sh
```

**Environment variables:**

| Key | Value |
|-----|--------|
| `DATABASE_URL` | Internal Database URL from Postgres |
| `DJANGO_SECRET_KEY` | long random string (see below) |
| `DEBUG` | `false` |
| `ALLOWED_HOSTS` | `*` or your `*.onrender.com` hostname |
| `DB_SSL_REQUIRE` | `false` (leave unset unless you know you need it) |

Do **not** set `PYTHONPATH=backend` when using `scripts/render_start.sh` (it sets `PYTHONPATH=.` inside `backend/`).

Generate a secret key:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

## API headers

All tenant-scoped routes require:

```
X-Tenant-Slug: acme-corp
```

## Key endpoints

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/ingest/SAP/` | Upload SAP CSV |
| POST | `/api/ingest/UTILITY/` | Upload utility CSV |
| POST | `/api/ingest/travel/sync/` | Mock travel API pull |
| GET | `/api/records/?status=FLAGGED` | Review queue |
| GET | `/api/records/{id}/` | Detail + raw payload |
| POST | `/api/records/{id}/review/` | `{ "action": "approve\|reject\|lock", "analyst": "..." }` |
| GET | `/api/audit/` | Audit log |

## Documentation

- [MODEL.md](./MODEL.md) — schema and traceability
- [DECISIONS.md](./DECISIONS.md) — why choices were made
- [TRADEOFFS.md](./TRADEOFFS.md) — omissions and scale limits
- [SOURCES.md](./SOURCES.md) — upstream field research

## Project layout

```
backend/
  config/          # Django settings
  tenants/         # Tenant model + middleware
  ingestion/       # Batches, raw records, upload API
  records/         # Normalized rows, flags, audit API
  services/        # Parsers, pipeline, normalization, anomalies
frontend/          # Analyst UI
sample_data/       # Realistic messy CSVs
```
