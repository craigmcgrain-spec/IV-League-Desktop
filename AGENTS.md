# AGENTS.md

PyQt6 desktop app for IV therapy business management (clients, procedure records, invoicing). Single package, no monorepo.

## Commands
- Run: `pip install -r requirements.txt && python main.py` — README's `pip install -r main.py` is a typo
- Smoke check: `python smoke_test.py` (offscreen, temp DB) after touching DB/UI code
- No test suite, linter, or formatter exists — don't go looking
- Python >=3.10 (CI builds with 3.12)

## Releases (CI is the primary path)
- Push a `v*` tag → `.github/workflows/build.yml` builds AppImage + Windows installer and publishes the GitHub release automatically
- Local fallback: `bash build_appimage.sh` (Linux), `bash build_windows.sh` (Windows), then Inno Setup on `installer/iv-league-setup.iss`
- When bumping versions, edit `VERSION=` in `build_appimage.sh` and `build_windows.sh` — the tag name drives release artifact names
- Build scripts `rm -rf` dist/, build/, and `*.spec` first — the spec file is always regenerated, never hand-edit it

## Architecture
- Entry: `main.py` → `iv_league/ui/main_window.py` (tabs: Data Entry, Search Records, Invoicing, Pricing, Facilities, Clinicians)
- `iv_league/ui/record_form.py` holds the shared record form: Data Entry subclasses it (`all_tasks=False`), Edit Record embeds it (`all_tasks=True`) — change field/collect logic there, not in the two callers
- `iv_league/database/` — SQLite schema, migrations, settings, backups; `iv_league/utils/` — CSV parser + PDF invoice generator; `iv_league/assets/` — icon + `style.qss` (missing assets print a warning but the app still runs)

## Database conventions
- All runtime data lives in `~/.iv_league/` (DB, `settings.json`, `backups/`) — never in the repo
- Prices live in the single `pricing` table (task_id → price); there is no per-category pricing
- Schema change: add a `_migrate_*()` function in `iv_league/database/db.py`, gate it with `_migration_applied()` / `_mark_migration_applied()`, and call it from `init_db()` — migrations run automatically at startup
- Connection is a module-level singleton via `get_connection()` (WAL mode) — don't open your own `sqlite3.connect`

## Integration
- Mobile-app CSV import (Data Entry → Import CSV); expected CSV columns documented in README
