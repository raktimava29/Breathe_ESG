import csv
import io
import re
from typing import Any

from services.ingestion.base import BaseIngestionParser

# Realistic SAP MM / fuel export header variants seen in enterprise exports
SAP_HEADER_ALIASES = {
    "plant": ["plant", "werks", "plant_code", "plant id"],
    "material": ["material", "matnr", "material_no", "material number"],
    "quantity": ["quantity", "qty", "menge", "consumption", "qty consumed"],
    "unit": ["unit", "uom", "meins", "unit of measure"],
    "posting_date": ["posting date", "budat", "posting_date", "document date"],
    "document": ["document", "belnr", "doc number", "purchase doc"],
    "vendor": ["vendor", "lifnr", "supplier"],
    "cost_center": ["cost center", "kostl", "cost_ctr"],
    "fuel_type": ["fuel type", "fuel_type", "product", "description"],
}


def _normalize_header(h: str) -> str:
    return re.sub(r"\s+", " ", h.strip().lower())


def _map_headers(fieldnames: list[str]) -> dict[str, str]:
    normalized = {_normalize_header(h): h for h in fieldnames}
    mapping = {}
    for canonical, aliases in SAP_HEADER_ALIASES.items():
        for alias in aliases:
            if alias in normalized:
                mapping[canonical] = normalized[alias]
                break
    return mapping


class SAPCsvParser(BaseIngestionParser):
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
                "_source": "SAP_CSV",
                "plant": row.get(col_map.get("plant", ""), "").strip(),
                "material": row.get(col_map.get("material", ""), "").strip(),
                "quantity_raw": row.get(col_map.get("quantity", ""), "").strip(),
                "unit_raw": row.get(col_map.get("unit", ""), "").strip(),
                "posting_date_raw": row.get(col_map.get("posting_date", ""), "").strip(),
                "document": row.get(col_map.get("document", ""), "").strip(),
                "vendor": row.get(col_map.get("vendor", ""), "").strip(),
                "cost_center": row.get(col_map.get("cost_center", ""), "").strip(),
                "fuel_type": row.get(col_map.get("fuel_type", ""), "").strip(),
                "_unmapped_columns": {
                    k: v for k, v in row.items() if v and k not in col_map.values()
                },
            }
            rows.append(payload)
        return rows
