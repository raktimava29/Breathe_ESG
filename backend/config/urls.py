from django.contrib import admin
from django.urls import include, path, re_path

from config.views import root

urlpatterns = [
    path("", root, name="root"),
    path("admin/", admin.site.urls),
    path("api/", include("ingestion.urls")),
    path("api/", include("records.urls")),
    path("api/", include("tenants.urls")),
    # React SPA deep links (e.g. /review/123) should return index.html when built.
    re_path(r"^(?!api/|admin/).*", root, name="spa-fallback"),
]
