from django.db import models

from tenants.models import Tenant
from tenants.querysets import TenantScopedManager


class SourceCategory(models.TextChoices):
    SAP = "SAP", "SAP fuel/procurement"
    UTILITY = "UTILITY", "Utility electricity"
    TRAVEL = "TRAVEL", "Corporate travel"


class DataSource(models.Model):
    """Configured upstream system for a tenant."""

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="data_sources")
    category = models.CharField(max_length=16, choices=SourceCategory.choices)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    config = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = TenantScopedManager()

    class Meta:
        unique_together = [("tenant", "category")]
        ordering = ["category"]

    def __str__(self):
        return f"{self.tenant.slug}:{self.category}"


class IngestionBatchStatus(models.TextChoices):
    RECEIVED = "RECEIVED", "Received"
    PROCESSING = "PROCESSING", "Processing"
    COMPLETED = "COMPLETED", "Completed"
    FAILED = "FAILED", "Failed"


class IngestionBatch(models.Model):
    """One upload or API pull — immutable metadata for traceability."""

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="batches")
    data_source = models.ForeignKey(
        DataSource, on_delete=models.PROTECT, related_name="batches"
    )
    status = models.CharField(
        max_length=16,
        choices=IngestionBatchStatus.choices,
        default=IngestionBatchStatus.RECEIVED,
    )
    filename = models.CharField(max_length=512, blank=True)
    uploaded_by = models.CharField(max_length=255, blank=True)
    record_count = models.PositiveIntegerField(default=0)
    error_summary = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    objects = TenantScopedManager()

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Batch {self.id} ({self.data_source.category})"


class RawRecord(models.Model):
    """
    Source-of-truth payload. Never updated after insert except
    optional linkage fields set during same transaction as insert.
    """

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="raw_records")
    batch = models.ForeignKey(IngestionBatch, on_delete=models.CASCADE, related_name="raw_records")
    data_source = models.ForeignKey(DataSource, on_delete=models.PROTECT)
    source_row_index = models.PositiveIntegerField()
    source_record_id = models.CharField(max_length=255, blank=True)
    payload = models.JSONField()
    payload_hash = models.CharField(max_length=64, db_index=True)
    ingested_at = models.DateTimeField(auto_now_add=True)

    objects = TenantScopedManager()

    class Meta:
        ordering = ["batch", "source_row_index"]
        indexes = [
            models.Index(fields=["tenant", "payload_hash"]),
        ]

    def __str__(self):
        return f"Raw {self.id} row={self.source_row_index}"
