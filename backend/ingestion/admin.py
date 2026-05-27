from django.contrib import admin

from ingestion.models import DataSource, IngestionBatch, RawRecord


@admin.register(DataSource)
class DataSourceAdmin(admin.ModelAdmin):
    list_display = ("tenant", "category", "name", "is_active")
    list_filter = ("category",)


@admin.register(IngestionBatch)
class IngestionBatchAdmin(admin.ModelAdmin):
    list_display = ("id", "tenant", "data_source", "status", "record_count", "created_at")
    list_filter = ("status",)


@admin.register(RawRecord)
class RawRecordAdmin(admin.ModelAdmin):
    list_display = ("id", "batch", "source_row_index", "source_record_id", "ingested_at")
    readonly_fields = ("payload", "payload_hash")
