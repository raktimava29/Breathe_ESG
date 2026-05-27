from decimal import Decimal

from records.models import UnitConversionMap


def normalize_unit(raw_unit: str | None) -> tuple[Decimal | None, str | None, list[str]]:
    """
    Convert quantity to canonical unit using reference map.
    Returns (canonical_quantity, canonical_unit, notes).
    """
    notes: list[str] = []
    if not raw_unit:
        return None, None, ["missing_unit"]

    key = raw_unit.strip()
    mapping = UnitConversionMap.objects.filter(source_unit__iexact=key).first()
    if not mapping:
        alt = key.upper().replace(" ", "_")
        mapping = UnitConversionMap.objects.filter(source_unit__iexact=alt).first()
    if not mapping:
        notes.append(f"unknown_unit:{raw_unit}")
        return None, raw_unit, notes

    return mapping.factor_to_canonical, mapping.canonical_unit, notes
