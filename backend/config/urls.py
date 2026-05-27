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
    # IMPORTANT: exclude static asset paths so JS/CSS aren't served as HTML.
    re_path(r"^(?!api/|admin/|static/|assets/).*", root, name="spa-fallback"),
]
