from django.db import transaction
from django.utils import timezone

from ingestion.models import (
    IngestionBatch,
    IngestionBatchStatus,
    RawRecord,
    SourceCategory,
)
from records.models import NormalizedEmissionRecord
from services.anomalies.detector import apply_anomaly_results, detect_anomalies
from services.audit import log_event
from services.ingestion.base import BaseIngestionParser, payload_hash
from services.ingestion.sap import SAPCsvParser
from services.ingestion.travel import TravelApiParser
from services.ingestion.utility import UtilityCsvParser
from services.normalization.sap import normalize_sap_record
from services.normalization.travel import normalize_travel_record
from services.normalization.utility import normalize_utility_record

PARSERS: dict[str, BaseIngestionParser] = {
    SourceCategory.SAP: SAPCsvParser(),
    SourceCategory.UTILITY: UtilityCsvParser(),
    SourceCategory.TRAVEL: TravelApiParser(),
}

NORMALIZERS = {
    SourceCategory.SAP: normalize_sap_record,
    SourceCategory.UTILITY: normalize_utility_record,
    SourceCategory.TRAVEL: normalize_travel_record,
}


@transaction.atomic
def run_ingestion_pipeline(
    *,
    batch: IngestionBatch,
    content: bytes | str | None = None,
    parser_metadata: dict | None = None,
    uploaded_by: str = "",
) -> IngestionBatch:
    tenant = batch.tenant
    category = batch.data_source.category
    parser = PARSERS.get(category)
    normalizer = NORMALIZERS.get(category)

    if not parser or not normalizer:
        batch.status = IngestionBatchStatus.FAILED
        batch.error_summary = f"No parser for category {category}"
        batch.save()
        return batch

    batch.status = IngestionBatchStatus.PROCESSING
    batch.uploaded_by = uploaded_by or batch.uploaded_by
    batch.save(update_fields=["status", "uploaded_by"])

    try:
        if category == SourceCategory.TRAVEL:
            rows = parser.parse_rows(b"", metadata=parser_metadata)
        else:
            if not content:
                raise ValueError("File content required for CSV sources.")
            rows = parser.parse_rows(content, metadata=parser_metadata)
    except Exception as exc:
        batch.status = IngestionBatchStatus.FAILED
        batch.error_summary = str(exc)
        batch.completed_at = timezone.now()
        batch.save()
        log_event(
            tenant=tenant,
            entity_type="IngestionBatch",
            entity_id=batch.id,
            action="INGESTION_FAILED",
            actor=uploaded_by,
            metadata={"error": str(exc)},
        )
        return batch

    raw_records = []
    for idx, payload in enumerate(rows):
        phash = payload_hash(payload)
        source_id = payload.get("document") or payload.get("booking_id") or payload.get("meter") or ""
        raw_records.append(
            RawRecord(
                tenant=tenant,
                batch=batch,
                data_source=batch.data_source,
                source_row_index=payload.get("_row_index", idx),
                source_record_id=str(source_id)[:255],
                payload=payload,
                payload_hash=phash,
            )
        )

    RawRecord.objects.bulk_create(raw_records)
    created_raw = list(
        RawRecord.objects.filter(batch=batch).order_by("source_row_index")
    )

    normalized = []
    for raw in created_raw:
        norm = normalizer(raw)
        normalized.append(norm)

    NormalizedEmissionRecord.objects.bulk_create(normalized)
    created_norm = list(
        NormalizedEmissionRecord.objects.filter(batch=batch).select_related("raw_record")
    )

    for norm in created_norm:
        flags = detect_anomalies(norm)
        apply_anomaly_results(norm, flags)

    batch.record_count = len(created_raw)
    batch.status = IngestionBatchStatus.COMPLETED
    batch.completed_at = timezone.now()
    batch.save()

    log_event(
        tenant=tenant,
        entity_type="IngestionBatch",
        entity_id=batch.id,
        action="INGESTION_COMPLETED",
        actor=uploaded_by,
        after_state={"record_count": batch.record_count, "status": batch.status},
    )
    return batch
