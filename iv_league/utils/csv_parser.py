import csv
import re
from datetime import datetime

GAUGE_PATTERN = re.compile(r"^(\d+ga)$")
ATTEMPTS_PATTERN = re.compile(r"^Attempts:\s*(\d+)$", re.IGNORECASE)
CAP_CHANGE_PATTERN = re.compile(r"^Cap change:\s*(Yes|No)$", re.IGNORECASE)
CAP_VALUES = {"yes": 1, "y": 1, "true": 1, "1": 1,
              "no": 0, "n": 0, "false": 0, "0": 0}
SIDE_OPTIONS = {"Left", "Right"}
SUPPLIES_PREFIX = "supplies"


def _row_get(row, header):
    """Case-insensitive header lookup with empty-string fallback."""
    if header in row:
        return row[header] or ""
    lowered = header.lower()
    for key in row:
        if key and key.lower() == lowered:
            return row[key] or ""
    return ""


def _to_float(value):
    cleaned = str(value).strip().replace("$", "").replace(",", "")
    if not cleaned:
        return 0.0
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def _to_cap_change(value):
    return CAP_VALUES.get(str(value).strip().lower(), 0)


def _parse_procedure_details(details):
    gauge = ""
    side = ""
    location = ""
    notes = ""
    cap_change = 0

    if not details:
        return gauge, side, location, notes, cap_change

    parts = [p.strip() for p in details.split("·")]

    for part in parts:
        if ATTEMPTS_PATTERN.match(part):
            continue

        if part.lower().startswith(SUPPLIES_PREFIX):
            continue

        cap_match = CAP_CHANGE_PATTERN.match(part)
        if cap_match:
            cap_change = 1 if cap_match.group(1).lower() == "yes" else 0
            continue

        gauge_match = GAUGE_PATTERN.match(part)

        tokens = part.split()
        if tokens and tokens[0] in SIDE_OPTIONS:
            side_match = tokens[0]
        else:
            side_match = None

        if gauge_match:
            gauge = gauge_match.group(1)
        elif side_match:
            side = side_match
            location = " ".join(tokens[1:])
        elif not side and not location:
            location = part
        else:
            notes = (notes + " · " + part).strip(" ·")

    if notes and not side and not location and not gauge:
        notes = ""
        location = details

    return gauge, side, location, notes, cap_change


def parse_csv(path):
    rows = []
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            return rows

        fieldnames = [h.strip() for h in reader.fieldnames if h]
        supply_headers = [
            h for h in fieldnames if h.lower().startswith(SUPPLIES_PREFIX)
        ]

        for row in reader:
            iso_time = _row_get(row, "Completed At (ISO 8601)").strip()
            task = _row_get(row, "Task").strip()
            client_name = _row_get(row, "Client Name").strip()
            facility = _row_get(row, "Facility").strip()
            room = _row_get(row, "Room Number").strip()
            details = _row_get(row, "Procedure Details").strip()
            clinician_name = _row_get(row, "Clinician Name").strip()
            clinician_cred = _row_get(row, "Clinician Credentials").strip()

            if not all([iso_time, task, client_name, facility]):
                continue

            date_str = ""
            time_str = ""
            if iso_time:
                try:
                    dt = datetime.fromisoformat(iso_time.replace("Z", "+00:00"))
                    date_str = dt.strftime("%Y-%m-%d")
                    time_str = dt.strftime("%H:%M")
                except ValueError:
                    continue

            gauge, side, location, notes, cap_change = _parse_procedure_details(details)

            # Direct columns override values parsed from Procedure Details
            gauge = _row_get(row, "Gauge").strip() or gauge
            side = _row_get(row, "Side").strip() or side
            location = _row_get(row, "Location").strip() or location
            notes = _row_get(row, "Notes").strip() or notes
            cap_direct = _row_get(row, "Cap Change").strip()
            if cap_direct:
                cap_change = _to_cap_change(cap_direct)

            parsed = {
                "facility": facility,
                "name": client_name,
                "date": date_str,
                "time": time_str,
                "task": task,
                "gauge": gauge,
                "side": side,
                "location": location,
                "notes": notes,
                "cap_change": cap_change,
                "room": room,
                "clinician_name": clinician_name,
                "clinician_credentials": clinician_cred,
            }

            # Supply quantity columns (any header starting with "Supplies")
            for header in supply_headers:
                parsed[header] = _to_float(_row_get(row, header))

            rows.append(parsed)
    return rows
