from pathlib import Path

from django.conf import settings
from django.http import FileResponse, JsonResponse


def root(request):
    # Single-service deploy: if a React build exists, serve it as the app shell.
    index_path = Path(settings.BASE_DIR).parent / "frontend" / "dist" / "index.html"
    if index_path.exists():
        return FileResponse(open(index_path, "rb"), content_type="text/html")

    return JsonResponse(
        {
            "service": "Breathe ESG API",
            "docs": "See README.md in the project root.",
            "ui": "Run the React app: cd frontend && npm run dev → http://localhost:5173",
            "endpoints": {
                "tenants": "/api/tenants/",
                "sources": "/api/sources/",
                "batches": "/api/batches/",
                "records": "/api/records/",
                "audit": "/api/audit/",
                "admin": "/admin/",
            },
            "tenant_header": "X-Tenant-Slug: acme-corp (required on /api/* except /api/tenants/)",
        }
    )
