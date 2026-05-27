from django.conf import settings
from django.http import JsonResponse

from tenants.context import set_current_tenant
from tenants.models import Tenant


class TenantMiddleware:
    """
    Resolve tenant from X-Tenant-Slug header.
    All API handlers assume tenant is set before DB access.
    """

    HEADER = "HTTP_X_TENANT_SLUG"

    def __init__(self, get_response):
        self.get_response = get_response

    EXEMPT_PREFIXES = ("/api/tenants/", "/admin/")

    def __call__(self, request):
        if any(request.path.startswith(p) for p in self.EXEMPT_PREFIXES):
            set_current_tenant(None)
            request.tenant = None
            return self.get_response(request)

        slug = request.META.get(self.HEADER) or getattr(
            settings, "DEFAULT_TENANT_SLUG", None
        )
        if request.path.startswith("/api/") and not slug:
            return JsonResponse(
                {"detail": "X-Tenant-Slug header required."},
                status=400,
            )

        tenant = None
        if slug:
            try:
                tenant = Tenant.objects.get(slug=slug)
            except Tenant.DoesNotExist:
                if request.path.startswith("/api/"):
                    return JsonResponse(
                        {"detail": f"Unknown tenant: {slug}"},
                        status=404,
                    )

        set_current_tenant(tenant)
        request.tenant = tenant
        response = self.get_response(request)
        return response
