import csv
import io
import re
from typing import Any

from services.ingestion.base import BaseIngestionParser

UTILITY_HEADER_ALIASES = {
    "account": ["account number", "account", "service account"],
    "meter": ["meter id", "meter", "meter number", "premise id"],
    "billing_start": ["bill period start", "period start", "service from", "from date"],
    "billing_end": ["bill period end", "period end", "service to", "to date"],
    "usage": ["usage", "consumption", "kwh", "energy (kwh)", "total kwh"],
    "unit": ["unit", "uom"],
    "tariff": ["rate schedule", "tariff", "rate class"],
    "charges": ["total charges", "amount due", "bill amount", "charges"],
    "utility_name": ["utility", "provider", "supplier name"],
}


def _normalize_header(h: str) -> str:
    return re.sub(r"\s+", " ", h.strip().lower())


def _map_headers(fieldnames: list[str]) -> dict[str, str]:
    normalized = {_normalize_header(h): h for h in fieldnames}
    mapping = {}
    for canonical, aliases in UTILITY_HEADER_ALIASES.items():
        for alias in aliases:
            if alias in normalized:
                mapping[canonical] = normalized[alias]
                break
    return mapping


class UtilityCsvParser(BaseIngestionParser):
    def parse_rows(self, content: bytes | str, metadata: dict | None = None) -> list[dict[str, Any]]:
        if isinstance(content, bytes):
            text = content.decode("utf-8-sig", errors="replace")
        else:
            text = content

        reader = csv.DictReader(io.StringIO(text))
        if not reader.fieldnames:
            return []

        col_map = _map_headers(list(reader.fieldnames))
        rows = []
        for idx, row in enumerate(reader):
            payload = {
                "_row_index": idx,
                "_source": "UTILITY_CSV",
                "account": row.get(col_map.get("account", ""), "").strip(),
                "meter": row.get(col_map.get("meter", ""), "").strip(),
                "billing_start_raw": row.get(col_map.get("billing_start", ""), "").strip(),
                "billing_end_raw": row.get(col_map.get("billing_end", ""), "").strip(),
                "usage_raw": row.get(col_map.get("usage", ""), "").strip(),
                "unit_raw": row.get(col_map.get("unit", ""), "kWh").strip(),
                "tariff": row.get(col_map.get("tariff", ""), "").strip(),
                "charges_raw": row.get(col_map.get("charges", ""), "").strip(),
                "utility_name": row.get(col_map.get("utility_name", ""), "").strip(),
                "_unmapped_columns": {
                    k: v for k, v in row.items() if v and k not in col_map.values()
                },
            }
            rows.append(payload)
        return rows
