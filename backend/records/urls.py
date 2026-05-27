from django.urls import path

from records.views import (
    AuditLogListView,
    RecordDetailView,
    RecordListView,
    RecordReviewView,
)

urlpatterns = [
    path("records/", RecordListView.as_view(), name="record-list"),
    path("records/<int:record_id>/", RecordDetailView.as_view(), name="record-detail"),
    path("records/<int:record_id>/review/", RecordReviewView.as_view(), name="record-review"),
    path("audit/", AuditLogListView.as_view(), name="audit-list"),
]
