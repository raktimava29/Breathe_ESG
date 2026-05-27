from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from ingestion.models import DataSource, IngestionBatch, RawRecord, SourceCategory
from ingestion.serializers import (
    DataSourceSerializer,
    IngestionBatchSerializer,
    RawRecordSerializer,
)
from services.ingestion.pipeline import run_ingestion_pipeline


class DataSourceListView(generics.ListAPIView):
    serializer_class = DataSourceSerializer

    def get_queryset(self):
        return DataSource.objects.all().order_by("category")


class IngestionBatchListView(generics.ListAPIView):
    serializer_class = IngestionBatchSerializer

    def get_queryset(self):
        return IngestionBatch.objects.all().select_related("data_source")


class RawRecordListView(generics.ListAPIView):
    serializer_class = RawRecordSerializer

    def get_queryset(self):
        batch_id = self.kwargs["batch_id"]
        return RawRecord.objects.filter(batch_id=batch_id).order_by("source_row_index")


class IngestUploadView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, category: str):
        tenant = request.tenant
        category = category.upper()
        if category not in SourceCategory.values:
            return Response({"detail": "Invalid category."}, status=400)

        data_source = get_object_or_404(
            DataSource, tenant=tenant, category=category, is_active=True
        )

        upload_file = request.FILES.get("file")
        uploaded_by = request.data.get("uploaded_by", "analyst")

        batch = IngestionBatch.objects.create(
            tenant=tenant,
            data_source=data_source,
            filename=upload_file.name if upload_file else "",
            uploaded_by=uploaded_by,
            metadata={"category": category},
        )

        content = upload_file.read() if upload_file else None
        if category == SourceCategory.TRAVEL:
            content = None

        if category != SourceCategory.TRAVEL and not content:
            batch.delete()
            return Response({"detail": "file is required for CSV sources."}, status=400)

        run_ingestion_pipeline(
            batch=batch,
            content=content,
            parser_metadata=request.data.dict() if hasattr(request.data, "dict") else {},
            uploaded_by=uploaded_by,
        )
        batch.refresh_from_db()
        return Response(
            IngestionBatchSerializer(batch).data,
            status=status.HTTP_201_CREATED,
        )


class TravelIngestView(APIView):
    """Mock API pull from corporate travel platform."""

    def post(self, request):
        tenant = request.tenant
        data_source = get_object_or_404(
            DataSource, tenant=tenant, category=SourceCategory.TRAVEL, is_active=True
        )
        limit = int(request.data.get("limit", 10))
        uploaded_by = request.data.get("uploaded_by", "system-sync")

        batch = IngestionBatch.objects.create(
            tenant=tenant,
            data_source=data_source,
            filename="travel_api_sync",
            uploaded_by=uploaded_by,
            metadata={"source": "mock_travel_api", "limit": limit},
        )

        run_ingestion_pipeline(
            batch=batch,
            parser_metadata={"limit": limit},
            uploaded_by=uploaded_by,
        )
        batch.refresh_from_db()
        return Response(
            IngestionBatchSerializer(batch).data,
            status=status.HTTP_201_CREATED,
        )
