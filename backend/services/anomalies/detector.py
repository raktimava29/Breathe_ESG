from decimal import Decimal

from django.db.models import Avg
from django.utils import timezone

from records.models import (
    ActivityCategory,
    AnomalyFlag,
    AnomalySeverity,
    NormalizedEmissionRecord,
    ReviewStatus,
)


THRESHOLDS = {
    ActivityCategory.PURCHASED_ELECTRICITY: Decimal("500000"),  # kWh
    ActivityCategory.STATIONARY_COMBUSTION: Decimal("100000"),  # liters
    ActivityCategory.MOBILE_COMBUSTION: Decimal("50000"),
    ActivityCategory.BUSINESS_TRAVEL_AIR: Decimal("15000"),  # km
}


def _flag(record, code, message, severity, context=None):
    return AnomalyFlag(
        tenant=record.tenant,
        record=record,
        rule_code=code,
        message=message,
        severity=severity,
        context=context or {},
    )


def detect_anomalies(record: NormalizedEmissionRecord) -> list[AnomalyFlag]:
    flags: list[AnomalyFlag] = []

    if record.quantity is not None and record.quantity < 0:
        flags.append(
            _flag(record, "NEGATIVE_QUANTITY", "Quantity is negative.", AnomalySeverity.HIGH)
        )

    if record.canonical_quantity is None and record.distance_km is None:
        flags.append(
            _flag(
                record,
                "MISSING_MANDATORY_QUANTITY",
                "No canonical quantity or distance available.",
                AnomalySeverity.HIGH,
            )
        )

    if not record.activity_date and not (record.period_start and record.period_end):
        flags.append(
            _flag(
                record,
                "MISSING_DATE",
                "No activity date or billing period.",
                AnomalySeverity.MEDIUM,
            )
        )

    if record.normalization_notes:
        for note in record.normalization_notes:
            if "unparseable" in note or "unknown_unit" in note or "distance_unknown" in note:
                flags.append(
                    _flag(
                        record,
                        "NORMALIZATION_WARNING",
                        f"Normalization issue: {note}",
                        AnomalySeverity.MEDIUM,
                        {"note": note},
                    )
                )

    threshold = THRESHOLDS.get(record.activity_category)
    if threshold and record.canonical_quantity and record.canonical_quantity > threshold:
        flags.append(
            _flag(
                record,
                "HIGH_CONSUMPTION",
                f"Canonical quantity {record.canonical_quantity} exceeds threshold {threshold}.",
                AnomalySeverity.HIGH,
                {"quantity": str(record.canonical_quantity), "threshold": str(threshold)},
            )
        )

    dup_hash = record.raw_record.payload_hash
    dupes = (
        NormalizedEmissionRecord.objects.unscoped()
        .filter(tenant=record.tenant, raw_record__payload_hash=dup_hash)
        .exclude(pk=record.pk)
        .count()
    )
    if dupes > 0:
        flags.append(
            _flag(
                record,
                "DUPLICATE_PAYLOAD",
                "Another normalized record shares the same raw payload hash.",
                AnomalySeverity.MEDIUM,
                {"duplicate_count": dupes},
            )
        )

    if record.activity_date and record.canonical_quantity:
        prior = (
            NormalizedEmissionRecord.objects.unscoped()
            .filter(
                tenant=record.tenant,
                activity_category=record.activity_category,
                site_code=record.site_code,
                activity_date__lt=record.activity_date,
                canonical_quantity__isnull=False,
            )
            .order_by("-activity_date")[:6]
        )
        if prior.exists():
            avg = prior.aggregate(avg=Avg("canonical_quantity"))["avg"]
            if avg and avg > 0:
                ratio = float(record.canonical_quantity / avg)
                if ratio > 3.0 or ratio < 0.33:
                    flags.append(
                        _flag(
                            record,
                            "MONTH_OVER_MONTH_VARIANCE",
                            f"Quantity deviates significantly from site average (ratio={ratio:.2f}).",
                            AnomalySeverity.MEDIUM,
                            {"ratio": ratio, "site_avg": str(avg)},
                        )
                    )

    return flags


def apply_anomaly_results(record: NormalizedEmissionRecord, flags: list[AnomalyFlag]):
    AnomalyFlag.objects.filter(record=record).delete()
    if flags:
        AnomalyFlag.objects.bulk_create(flags)
        if record.status == ReviewStatus.PENDING:
            record.status = ReviewStatus.FLAGGED
            record.save(update_fields=["status", "updated_at"])
    elif record.status == ReviewStatus.FLAGGED:
        record.status = ReviewStatus.PENDING
        record.save(update_fields=["status", "updated_at"])
