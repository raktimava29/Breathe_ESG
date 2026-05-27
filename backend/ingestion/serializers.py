from rest_framework import serializers

from ingestion.models import DataSource, IngestionBatch, RawRecord


class DataSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataSource
        fields = ("id", "category", "name", "is_active", "created_at")


class IngestionBatchSerializer(serializers.ModelSerializer):
    data_source = DataSourceSerializer(read_only=True)

    class Meta:
        model = IngestionBatch
        fields = (
            "id",
            "data_source",
            "status",
            "filename",
            "uploaded_by",
            "record_count",
            "error_summary",
            "metadata",
            "created_at",
            "completed_at",
        )


class RawRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = RawRecord
        fields = (
            "id",
            "source_row_index",
            "source_record_id",
            "payload",
            "payload_hash",
            "ingested_at",
            "batch_id",
        )
