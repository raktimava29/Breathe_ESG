# Source research notes

Research informed field names and parser alias maps — not full vendor certification.

## SAP MM / fuel & procurement exports

**Typical delivery:** Scheduled CSV/flat file from SAP MM or BW extract; headers vary by client (English vs German labels).

**Fields referenced:**
- `Plant` / `Werks` — site attribution
- `Material` / `MATNR` — fuel/material id
- `Quantity` / `Menge` + `Unit` / `MEINS` — UoM inconsistencies (L, GAL)
- `Posting date` / `BUDAT` — multiple date formats in one file
- `Document` / `BELNR` — trace key
- `Vendor` / `LIFNR`, `Cost Center` / `KOSTL`

**Messiness modeled in sample data:**
- Comma thousands separators
- US vs EU dates in same export
- Duplicate row (same document/qty) for duplicate detection demo
- Missing vendor on one row

**Scope mapping assumption:** Stationary vs mobile combustion inferred from fuel type keywords → Scope 1.

## Utility electricity portal exports

**Typical delivery:** CSV from utility customer portal (PG&E, ConEd style column naming).

**Fields referenced:**
- Account / meter identifiers
- **Non-calendar billing periods** (`Service From` / `Service To`)
- `Total kWh` usage
- Rate schedule / tariff code
- Amount due

**Messiness modeled:**
- Billing period stored as `period_start` / `period_end` on normalized row
- Inverted period check in normalization notes (not in sample but rule exists)
- kWh with comma formatting

**Scope mapping:** Purchased electricity → Scope 2.

## Corporate travel (Concur / Navan style)

**Typical delivery:** REST API or expense export with trip segments.

**Fields referenced:**
- `booking_id`, `employee_id`, `trip_type` (flight / hotel / ground)
- Airport codes for flights; missing `distance_km` common
- European date format on one booking (`15/05/2024`)
- USD amounts as strings

**Distance handling:** Static airport-pair lookup table for SFO-JFK, LHR-CDG; unknown pairs flagged.

**Scope mapping:** Business travel categories → Scope 3.

## Sample files

- `sample_data/sap_fuel_export.csv`
- `sample_data/utility_billing.csv`
- Travel: mock data in `services/ingestion/travel.py`

## References (informal)

- SAP field naming: SAP Help Portal / community MM tables (general knowledge)
- Utility CSV patterns: common US utility bill download layouts
- Travel API shapes: SAP Concur expense report and trip resource documentation (high level)
