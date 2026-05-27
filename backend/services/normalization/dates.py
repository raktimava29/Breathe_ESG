from datetime import date, datetime

from dateutil import parser as date_parser


def parse_flexible_date(raw: str | None) -> date | None:
    if not raw or not str(raw).strip():
        return None
    text = str(raw).strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d.%m.%Y", "%Y%m%d"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    try:
        return date_parser.parse(text, dayfirst=False).date()
    except (ValueError, TypeError):
        return None
