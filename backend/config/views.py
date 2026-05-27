from django.http import JsonResponse


def root(request):
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
