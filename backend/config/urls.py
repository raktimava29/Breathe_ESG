from django.contrib import admin
from django.urls import include, path

from config.views import root

urlpatterns = [
    path("", root, name="root"),
    path("admin/", admin.site.urls),
    path("api/", include("ingestion.urls")),
    path("api/", include("records.urls")),
    path("api/", include("tenants.urls")),
]
