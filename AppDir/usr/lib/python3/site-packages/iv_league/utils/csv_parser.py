import csv
import re
from datetime import datetime

GAUGE_PATTERN = re.compile(r"^(\d+ga)$")
ATTEMPTS_PATTERN = re.compile(r"^Attempts:\s*(\d+)$", re.IGNORECASE)
CAP_CHANGE_PATTERN = re.compile(r"^Cap change:\s*(Yes|No)$", re.IGNORECASE)
SIDE_OPTIONS = {"Left", "Right"}


def _parse_procedure_details(details):
    gauge = ""
    side = ""
    location = ""
    notes = ""
    attempts = None
    cap_change = 0

    if not details:
        return gauge, side, location, notes, attempts, cap_change

    parts = [p.strip() for p in details.split("·")]

    for part in parts:
        attempts_match = ATTEMPTS_PATTERN.match(part)
        if attempts_match:
            attempts = int(attempts_match.group(1))
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

    return gauge, side, location, notes, attempts, cap_change


def parse_csv(path):
    rows = []
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            return rows

        for row in reader:
            iso_time = row.get("Completed At (ISO 8601)", "").strip()
            task = row.get("Task", "").strip()
            client_name = row.get("Client Name", "").strip()
            facility = row.get("Facility", "").strip()
            room = row.get("Room Number", "").strip()
            details = row.get("Procedure Details", "").strip()
            clinician_name = row.get("Clinician Name", "").strip()
            clinician_cred = row.get("Clinician Credentials", "").strip()

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

            gauge, side, location, notes, attempts, cap_change = _parse_procedure_details(details)

            rows.append({
                "facility": facility,
                "name": client_name,
                "date": date_str,
                "time": time_str,
                "task": task,
                "gauge": gauge,
                "side": side,
                "location": location,
                "notes": notes,
                "attempts": attempts,
                "cap_change": cap_change,
                "room": room,
                "clinician_name": clinician_name,
                "clinician_credentials": clinician_cred,
            })
    return rows
