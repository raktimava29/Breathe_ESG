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


def normalize_utility_record(raw: RawRecord) -> NormalizedEmissionRecord:
    p = raw.payload
    notes: list = []

    qty = _parse_decimal(p.get("usage_raw"))
    unit_raw = (p.get("unit_raw") or "kWh").strip()
    factor, canonical_unit, unit_notes = normalize_unit(unit_raw)
    notes.extend(unit_notes)

    canonical_qty = qty * factor if qty is not None and factor else qty

    period_start = parse_flexible_date(p.get("billing_start_raw"))
    period_end = parse_flexible_date(p.get("billing_end_raw"))
    if p.get("billing_start_raw") and not period_start:
        notes.append("unparseable_billing_start")
    if p.get("billing_end_raw") and not period_end:
        notes.append("unparseable_billing_end")
    if period_start and period_end and period_end < period_start:
        notes.append("billing_period_inverted")

    activity_date = period_end or period_start

    return NormalizedEmissionRecord(
        tenant=raw.tenant,
        raw_record=raw,
        batch=raw.batch,
        data_source=raw.data_source,
        scope=EmissionScope.SCOPE_2,
        activity_category=ActivityCategory.PURCHASED_ELECTRICITY,
        activity_date=activity_date,
        period_start=period_start,
        period_end=period_end,
        site_code=p.get("meter") or p.get("account") or "",
        description=f"{p.get('utility_name', '')} {p.get('tariff', '')}".strip(),
        quantity=qty,
        quantity_unit=unit_raw,
        canonical_quantity=canonical_qty,
        canonical_unit=canonical_unit or "kWh",
        currency_amount=_parse_decimal(p.get("charges_raw")),
        source_fields=p,
        normalization_notes=notes,
    )
