from django.db import models

from tenants.context import get_current_tenant


class TenantScopedQuerySet(models.QuerySet):
    def for_tenant(self, tenant=None):
        from tenants.context import get_current_tenant

        tenant = tenant or get_current_tenant()
        if tenant is None:
            return self.none()
        return self.filter(tenant=tenant)


class TenantScopedManager(models.Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        tenant = get_current_tenant()
        if tenant is not None and hasattr(self.model, "tenant"):
            qs = qs.filter(tenant=tenant)
        return qs

    def unscoped(self):
        return super().get_queryset()
