from decimal import Decimal, InvalidOperation

from records.models import (
    ActivityCategory,
    EmissionScope,
    NormalizedEmissionRecord,
    RawRecord,
)
from services.normalization.dates import parse_flexible_date
from services.units import normalize_unit


def _parse_decimal(raw: str | None) -> Decimal | None:
    if not raw:
        return None
    cleaned = str(raw).replace(",", "").strip()
    try:
        return Decimal(cleaned)
    except InvalidOperation:
        return None


def normalize_sap_record(raw: RawRecord) -> NormalizedEmissionRecord:
    p = raw.payload
    notes: list = []
    qty = _parse_decimal(p.get("quantity_raw"))
    unit_raw = (p.get("unit_raw") or "").strip()
    factor, canonical_unit, unit_notes = normalize_unit(unit_raw)
    notes.extend(unit_notes)

    canonical_qty = None
    if qty is not None and factor is not None:
        canonical_qty = qty * factor
    elif qty is not None:
        canonical_qty = qty

    activity_date = parse_flexible_date(p.get("posting_date_raw"))
    if p.get("posting_date_raw") and not activity_date:
        notes.append("unparseable_posting_date")

    fuel = (p.get("fuel_type") or "").lower()
    if "diesel" in fuel or "gasoline" in fuel or "fleet" in fuel:
        category = ActivityCategory.MOBILE_COMBUSTION
    else:
        category = ActivityCategory.STATIONARY_COMBUSTION

    return NormalizedEmissionRecord(
        tenant=raw.tenant,
        raw_record=raw,
        batch=raw.batch,
        data_source=raw.data_source,
        scope=EmissionScope.SCOPE_1,
        activity_category=category,
        activity_date=activity_date,
        site_code=p.get("plant") or "",
        description=p.get("fuel_type") or p.get("material") or "",
        quantity=qty,
        quantity_unit=unit_raw,
        canonical_quantity=canonical_qty,
        canonical_unit=canonical_unit or unit_raw,
        source_fields=p,
        normalization_notes=notes,
    )
