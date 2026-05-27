from typing import Any

from services.ingestion.base import BaseIngestionParser

# Mock Concur / Navan-style travel API response shape
MOCK_TRAVEL_BOOKINGS = [
    {
        "booking_id": "TRV-2024-00182",
        "employee_id": "E10492",
        "trip_type": "flight",
        "origin_airport": "SFO",
        "destination_airport": "JFK",
        "departure_date": "2024-03-14",
        "return_date": "2024-03-18",
        "distance_km": None,
        "class_of_service": "economy",
        "amount_usd": "842.50",
        "vendor": "United Airlines",
    },
    {
        "booking_id": "TRV-2024-00195",
        "employee_id": "E10221",
        "trip_type": "hotel",
        "city": "Chicago",
        "check_in": "2024-04-02",
        "check_out": "2024-04-05",
        "nights": 3,
        "amount_usd": "612.00",
        "vendor": "Marriott",
    },
    {
        "booking_id": "TRV-2024-00201",
        "employee_id": "E10877",
        "trip_type": "ground",
        "origin": "Boston Logan",
        "destination": "Providence RI",
        "travel_date": "2024-04-11",
        "distance_km": 80,
        "amount_usd": "145.00",
        "vendor": "Uber for Business",
    },
    {
        "booking_id": "TRV-2024-00215",
        "employee_id": "E10492",
        "trip_type": "flight",
        "origin_airport": "LHR",
        "destination_airport": "CDG",
        "departure_date": "15/05/2024",
        "return_date": None,
        "distance_km": None,
        "class_of_service": "business",
        "amount_usd": "1250.00",
        "vendor": "Air France",
    },
]


class TravelApiParser(BaseIngestionParser):
    """Simulates pulling bookings from a corporate travel platform API."""

    def parse_rows(self, content: bytes | str, metadata: dict | None = None) -> list[dict[str, Any]]:
        meta = metadata or {}
        limit = meta.get("limit", len(MOCK_TRAVEL_BOOKINGS))
        rows = []
        for idx, booking in enumerate(MOCK_TRAVEL_BOOKINGS[:limit]):
            payload = {**booking, "_row_index": idx, "_source": "TRAVEL_API"}
            rows.append(payload)
        return rows
