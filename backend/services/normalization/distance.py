from decimal import Decimal

# Approximate great-circle distances (km) for common missing-distance flight pairs
AIRPORT_DISTANCE_KM = {
    ("SFO", "JFK"): Decimal("4150"),
    ("JFK", "SFO"): Decimal("4150"),
    ("LHR", "CDG"): Decimal("344"),
    ("CDG", "LHR"): Decimal("344"),
    ("LAX", "ORD"): Decimal("2800"),
}


def estimate_flight_distance_km(origin: str | None, dest: str | None) -> tuple[Decimal | None, list[str]]:
    notes = []
    if not origin or not dest:
        return None, ["missing_airport_codes"]
    key = (origin.strip().upper(), dest.strip().upper())
    dist = AIRPORT_DISTANCE_KM.get(key)
    if dist:
        notes.append(f"distance_estimated:{key[0]}-{key[1]}")
        return dist, notes
    notes.append(f"distance_unknown:{key[0]}-{key[1]}")
    return None, notes
