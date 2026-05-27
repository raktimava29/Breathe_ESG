from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from records.models import AuditLog, NormalizedEmissionRecord, ReviewStatus
from records.serializers import (
    AuditLogSerializer,
    NormalizedRecordDetailSerializer,
    NormalizedRecordListSerializer,
    ReviewActionSerializer,
)
from services.review.workflow import transition_record


class RecordListView(generics.ListAPIView):
    serializer_class = NormalizedRecordListSerializer

    def get_queryset(self):
        qs = NormalizedEmissionRecord.objects.all().prefetch_related("flags")
        status_filter = self.request.query_params.get("status")
        if status_filter:
            qs = qs.filter(status=status_filter.upper())
        category = self.request.query_params.get("category")
        if category:
            qs = qs.filter(activity_category=category.upper())
        batch_id = self.request.query_params.get("batch")
        if batch_id:
            qs = qs.filter(batch_id=batch_id)
        return qs.order_by("-created_at")


class RecordDetailView(generics.RetrieveAPIView):
    serializer_class = NormalizedRecordDetailSerializer
    lookup_url_kwarg = "record_id"

    def get_queryset(self):
        return NormalizedEmissionRecord.objects.select_related(
            "raw_record", "batch", "data_source"
        ).prefetch_related("flags", "decisions")


class RecordReviewView(APIView):
    def post(self, request, record_id: int):
        record = get_object_or_404(NormalizedEmissionRecord, pk=record_id)
        ser = ReviewActionSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        action = ser.validated_data["action"]
        analyst = ser.validated_data["analyst"]
        comment = ser.validated_data.get("comment", "")

        mapping = {
            "approve": ReviewStatus.APPROVED,
            "reject": ReviewStatus.PENDING,
            "lock": ReviewStatus.LOCKED,
        }
        new_status = mapping[action]
        if record.status == ReviewStatus.FLAGGED and action == "approve":
            new_status = ReviewStatus.APPROVED

        try:
            transition_record(
                record=record,
                new_status=new_status,
                analyst=analyst,
                comment=comment,
            )
        except ValidationError as exc:
            return Response({"detail": str(exc)}, status=400)

        record.refresh_from_db()
        return Response(NormalizedRecordDetailSerializer(record).data)


class AuditLogListView(generics.ListAPIView):
    serializer_class = AuditLogSerializer

    def get_queryset(self):
        qs = AuditLog.objects.all()
        entity_type = self.request.query_params.get("entity_type")
        entity_id = self.request.query_params.get("entity_id")
        if entity_type:
            qs = qs.filter(entity_type=entity_type)
        if entity_id:
            qs = qs.filter(entity_id=entity_id)
        return qs.order_by("-created_at")[:200]
