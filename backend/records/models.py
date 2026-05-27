from django.core.exceptions import ValidationError
from django.db import models

from ingestion.models import DataSource, IngestionBatch, RawRecord
from tenants.models import Tenant
from tenants.querysets import TenantScopedManager


class EmissionScope(models.TextChoices):
    SCOPE_1 = "SCOPE_1", "Scope 1"
    SCOPE_2 = "SCOPE_2", "Scope 2"
    SCOPE_3 = "SCOPE_3", "Scope 3"


class ActivityCategory(models.TextChoices):
    STATIONARY_COMBUSTION = "STATIONARY_COMBUSTION", "Stationary combustion"
    MOBILE_COMBUSTION = "MOBILE_COMBUSTION", "Mobile combustion"
    PURCHASED_ELECTRICITY = "PURCHASED_ELECTRICITY", "Purchased electricity"
    BUSINESS_TRAVEL_AIR = "BUSINESS_TRAVEL_AIR", "Business travel — air"
    BUSINESS_TRAVEL_HOTEL = "BUSINESS_TRAVEL_HOTEL", "Business travel — hotel"
    BUSINESS_TRAVEL_GROUND = "BUSINESS_TRAVEL_GROUND", "Business travel — ground"


class ReviewStatus(models.TextChoices):
    PENDING = "PENDING", "Pending review"
    FLAGGED = "FLAGGED", "Flagged — needs attention"
    APPROVED = "APPROVED", "Approved"
    LOCKED = "LOCKED", "Locked (audit-ready)"


class UnitConversionMap(models.Model):
    """Reference table for unit normalization — not tenant-specific."""

    source_unit = models.CharField(max_length=32, db_index=True)
    canonical_unit = models.CharField(max_length=32)
    factor_to_canonical = models.DecimalField(max_digits=20, decimal_places=10)
    notes = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = [("source_unit", "canonical_unit")]

    def __str__(self):
        return f"{self.source_unit} -> {self.canonical_unit} x{self.factor_to_canonical}"


class NormalizedEmissionRecord(models.Model):
    """Canonical internal row — always traceable to RawRecord."""

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="emission_records")
    raw_record = models.OneToOneField(
        RawRecord, on_delete=models.PROTECT, related_name="normalized"
    )
    batch = models.ForeignKey(IngestionBatch, on_delete=models.PROTECT)
    data_source = models.ForeignKey(DataSource, on_delete=models.PROTECT)

    scope = models.CharField(max_length=16, choices=EmissionScope.choices)
    activity_category = models.CharField(max_length=32, choices=ActivityCategory.choices)

    activity_date = models.DateField(null=True, blank=True)
    period_start = models.DateField(null=True, blank=True)
    period_end = models.DateField(null=True, blank=True)

    site_code = models.CharField(max_length=64, blank=True)
    description = models.CharField(max_length=512, blank=True)

    quantity = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True)
    quantity_unit = models.CharField(max_length=32, blank=True)
    canonical_quantity = models.DecimalField(
        max_digits=20, decimal_places=6, null=True, blank=True
    )
    canonical_unit = models.CharField(max_length=32, blank=True)

    distance_km = models.DecimalField(
        max_digits=12, decimal_places=3, null=True, blank=True
    )
    currency_amount = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )

    source_fields = models.JSONField(default=dict)
    normalization_notes = models.JSONField(default=list)

    status = models.CharField(
        max_length=16,
        choices=ReviewStatus.choices,
        default=ReviewStatus.PENDING,
    )
    reviewed_by = models.CharField(max_length=255, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_comment = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = TenantScopedManager()

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["tenant", "status"]),
            models.Index(fields=["tenant", "activity_date"]),
        ]

    def save(self, *args, **kwargs):
        if self.pk:
            previous = NormalizedEmissionRecord.objects.unscoped().get(pk=self.pk)
            if previous.status == ReviewStatus.LOCKED:
                raise ValidationError("Locked records cannot be modified.")
            if previous.status == ReviewStatus.APPROVED and self.status != ReviewStatus.LOCKED:
                allowed = {
                    "status", "reviewed_by", "reviewed_at", "review_comment", "updated_at"
                }
                for field in self._meta.fields:
                    fname = field.name
                    if fname in allowed:
                        continue
                    if getattr(self, fname) != getattr(previous, fname):
                        raise ValidationError(
                            "Approved records are immutable except lock transition."
                        )
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Norm {self.id} {self.activity_category} [{self.status}]"


class AnomalySeverity(models.TextChoices):
    LOW = "LOW", "Low"
    MEDIUM = "MEDIUM", "Medium"
    HIGH = "HIGH", "High"


class AnomalyFlag(models.Model):
    """Explainable rule hits — separate from status for audit clarity."""

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="anomaly_flags")
    record = models.ForeignKey(
        NormalizedEmissionRecord,
        on_delete=models.CASCADE,
        related_name="flags",
    )
    rule_code = models.CharField(max_length=64)
    message = models.TextField()
    severity = models.CharField(max_length=8, choices=AnomalySeverity.choices)
    context = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    objects = TenantScopedManager()

    class Meta:
        ordering = ["-created_at"]


class ReviewDecision(models.Model):
    """Explicit analyst action — complements AuditLog."""

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="review_decisions")
    record = models.ForeignKey(
        NormalizedEmissionRecord,
        on_delete=models.CASCADE,
        related_name="decisions",
    )
    previous_status = models.CharField(max_length=16, choices=ReviewStatus.choices)
    new_status = models.CharField(max_length=16, choices=ReviewStatus.choices)
    analyst = models.CharField(max_length=255)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = TenantScopedManager()


class AuditLog(models.Model):
    """Append-only event stream for compliance traceability."""

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="audit_logs")
    entity_type = models.CharField(max_length=64)
    entity_id = models.PositiveIntegerField()
    action = models.CharField(max_length=64)
    actor = models.CharField(max_length=255, blank=True)
    before_state = models.JSONField(null=True, blank=True)
    after_state = models.JSONField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = TenantScopedManager()

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["tenant", "entity_type", "entity_id"]),
        ]
