# IV League Desktop

Desktop application for IV therapy business management. Tracks clients, procedures, and invoicing with a mobile app integration via CSV import.

## Features

- **Client Management** — Contact details, facility assignment
- **Procedure Tracking** — Import from mobile app CSV, track gauge, location, attempts, cap changes
- **Invoice Generation** — Professional 2-page PDF with company info and itemized procedures
- **Pricing Configuration** — Set per-task prices used in invoice calculations
- **Facility Directory** — Full contact info for each facility
- **Clinician Management** — Credentials and default clinician selection

## Installation

### Pre-built Binaries

Download the latest release from [GitHub Releases](https://github.com/craigmcgrain-spec/IV-League-Desktop/releases).

- **Linux**: Download `IVLeague-v1.0.0-x86_64.AppImage`, make executable (`chmod +x`), and run
- **Windows**: Download `IVLeague-Setup-1.0.0.exe` and run the installer

### Run from Source

```bash
pip install -r main.py
python main.py
```

## Building

### Linux (AppImage)

Requires: Python 3.10+, pip

```bash
pip install pyinstaller PyQt6 reportlab
bash build_appimage.sh
```

Output: `IVLeague-v1.0.0-x86_64.AppImage`

### Windows (.exe)

Requires: Python 3.10+, pip

```batch
build_windows.bat
```

Output: `dist\IVLeague.exe`

To create an installer:
1. Download [Inno Setup](https://jrsoftware.org/isinfo.php)
2. Open `installer\iv-league-setup.iss`
3. Build > Compile

Output: `installer\IVLeague-Setup-1.0.0.exe`

## Mobile App Integration

Import procedures from the [IV League Mobile](https://github.com/craigmcgrain-spec/IV-League-Mobile) app:

1. Export CSV from the mobile app
2. In Desktop app, go to **Data Entry** tab
3. Click **Import CSV**
4. Select the exported CSV file

CSV format: `Completed At, Task, Clinician Name, Clinician Credentials, Client Name, Facility, Room Number, Procedure Details`

## Tech Stack

- Python 3.10+
- PyQt6
- SQLite
- ReportLab (PDF generation)
- PyInstaller (packaging)

## License

MIT License — see [LICENSE](LICENSE)
