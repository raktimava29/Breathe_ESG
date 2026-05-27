from decimal import Decimal, InvalidOperation

from records.models import (
    ActivityCategory,
    EmissionScope,
    NormalizedEmissionRecord,
    RawRecord,
)
from services.normalization.dates import parse_flexible_date
from services.normalization.distance import estimate_flight_distance_km


def _parse_decimal(raw) -> Decimal | None:
    if raw is None:
        return None
    try:
        return Decimal(str(raw).replace(",", ""))
    except InvalidOperation:
        return None


def normalize_travel_record(raw: RawRecord) -> NormalizedEmissionRecord:
    p = raw.payload
    notes: list = []
    trip_type = (p.get("trip_type") or "").lower()

    if trip_type == "flight":
        category = ActivityCategory.BUSINESS_TRAVEL_AIR
        activity_date = parse_flexible_date(p.get("departure_date"))
        dist = p.get("distance_km")
        distance_km = _parse_decimal(dist) if dist is not None else None
        if distance_km is None:
            distance_km, dist_notes = estimate_flight_distance_km(
                p.get("origin_airport"), p.get("destination_airport")
            )
            notes.extend(dist_notes)
        description = f"{p.get('origin_airport', '')} -> {p.get('destination_airport', '')}"
    elif trip_type == "hotel":
        category = ActivityCategory.BUSINESS_TRAVEL_HOTEL
        activity_date = parse_flexible_date(p.get("check_in"))
        distance_km = None
        description = f"Hotel {p.get('city', '')} {p.get('nights', '')} nights"
    else:
        category = ActivityCategory.BUSINESS_TRAVEL_GROUND
        activity_date = parse_flexible_date(p.get("travel_date"))
        distance_km = _parse_decimal(p.get("distance_km"))
        description = f"{p.get('origin', '')} -> {p.get('destination', '')}"

    if not activity_date and p.get("departure_date"):
        notes.append("unparseable_travel_date")

    return NormalizedEmissionRecord(
        tenant=raw.tenant,
        raw_record=raw,
        batch=raw.batch,
        data_source=raw.data_source,
        scope=EmissionScope.SCOPE_3,
        activity_category=category,
        activity_date=activity_date,
        site_code=p.get("employee_id") or "",
        description=description,
        distance_km=distance_km,
        currency_amount=_parse_decimal(p.get("amount_usd")),
        source_fields=p,
        normalization_notes=notes,
    )
