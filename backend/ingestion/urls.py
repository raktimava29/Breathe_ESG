from django.urls import path

from ingestion.views import (
    DataSourceListView,
    IngestUploadView,
    IngestionBatchListView,
    RawRecordListView,
    TravelIngestView,
)

urlpatterns = [
    path("sources/", DataSourceListView.as_view(), name="data-sources"),
    path("batches/", IngestionBatchListView.as_view(), name="batch-list"),
    path("batches/<int:batch_id>/raw/", RawRecordListView.as_view(), name="batch-raw"),
    path("ingest/travel/sync/", TravelIngestView.as_view(), name="travel-sync"),
    path("ingest/<str:category>/", IngestUploadView.as_view(), name="ingest-upload"),
]
