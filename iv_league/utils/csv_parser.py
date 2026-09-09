import csv
from datetime import datetime


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

            side = ""
            location = ""
            notes = details
            if "·" in details:
                parts = details.split("·", 1)
                side_loc = parts[0].strip()
                notes = parts[1].strip() if len(parts) > 1 else ""
                tokens = side_loc.split()
                if tokens and tokens[0] in ("Left", "Right"):
                    side = tokens[0]
                    location = " ".join(tokens[1:])
                else:
                    location = side_loc

            rows.append({
                "facility": facility,
                "name": client_name,
                "date": date_str,
                "time": time_str,
                "task": task,
                "gauge": "",
                "side": side,
                "location": location,
                "notes": notes,
                "room": room,
            })
    return rows
