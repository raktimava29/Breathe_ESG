from django.urls import path

from tenants.views import TenantListView

urlpatterns = [
    path("tenants/", TenantListView.as_view(), name="tenant-list"),
]
