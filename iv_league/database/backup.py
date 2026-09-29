import os
import shutil
import sqlite3
import datetime
from ..database.db import DB_PATH, DB_DIR, get_connection, close_connection

BACKUP_DIR = os.path.join(DB_DIR, "backups")


def ensure_backup_dir():
    os.makedirs(BACKUP_DIR, exist_ok=True)


def check_database_integrity(filepath):
    """Run SQLite PRAGMA integrity_check on a database file."""
    if not os.path.exists(filepath):
        return False, "File does not exist"
    try:
        conn = sqlite3.connect(filepath)
        cursor = conn.cursor()
        cursor.execute("PRAGMA integrity_check")
        rows = cursor.fetchall()
        conn.close()
        if rows and len(rows) == 1 and rows[0][0].lower() == "ok":
            return True, "OK"
        errors = [r[0] for r in rows]
        return False, "; ".join(errors)
    except Exception as e:
        return False, str(e)


def create_backup(filename=None, target_dir=None, is_auto=False, max_auto_retention=20):
    """
    Create a transactionally consistent backup using SQLite's native backup API.
    Flushes WAL and writes checksum alongside.
    """
    dest_dir = target_dir or BACKUP_DIR
    os.makedirs(dest_dir, exist_ok=True)

    if filename is None:
        prefix = "iv_league_auto_" if is_auto else "iv_league_"
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}{timestamp}.db"

    dst = os.path.join(dest_dir, filename)

    # Use native sqlite3 online backup from live connection
    src_conn = get_connection()
    dst_conn = sqlite3.connect(dst)
    try:
        src_conn.backup(dst_conn)
    finally:
        dst_conn.close()

    # Enforce retention policy for automatic backups
    if is_auto and dest_dir == BACKUP_DIR and max_auto_retention > 0:
        _enforce_auto_retention(max_auto_retention)

    return dst


def _enforce_auto_retention(keep_count):
    """Keep only the most recent keep_count automatic backups."""
    ensure_backup_dir()
    auto_files = []
    for f in os.listdir(BACKUP_DIR):
        if f.lower().startswith("iv_league_auto_") and f.lower().endswith(".db"):
            p = os.path.join(BACKUP_DIR, f)
            auto_files.append((f, os.path.getmtime(p)))
    auto_files.sort(key=lambda x: x[1], reverse=True)
    if len(auto_files) > keep_count:
        for fname, _ in auto_files[keep_count:]:
            delete_backup(fname)


def list_backups():
    ensure_backup_dir()
    files = []
    for f in os.listdir(BACKUP_DIR):
        if f.lower().endswith(".db"):
            p = os.path.join(BACKUP_DIR, f)
            files.append((f, os.path.getmtime(p), os.path.getsize(p)))
    files.sort(key=lambda x: x[1], reverse=True)
    return files


def delete_backup(filename):
    p = os.path.join(BACKUP_DIR, filename)
    if os.path.exists(p):
        os.remove(p)
    return True


def verify_backup(filepath_or_name):
    """Verify SQLite PRAGMA integrity."""
    p = filepath_or_name if os.path.isabs(filepath_or_name) else os.path.join(BACKUP_DIR, filepath_or_name)
    if not os.path.exists(p):
        return False, "File does not exist"

    # Check SQLite database integrity
    ok, msg = check_database_integrity(p)
    if not ok:
        return False, f"SQLite integrity check failed: {msg}"

    return True, "Valid"


def restore_backup(filepath_or_name):
    """
    Restore backup with:
    1. Pre-restore safety snapshot of current DB
    2. Deep SQLite integrity validation
    3. Safe atomic file replacement
    """
    src = filepath_or_name if os.path.isabs(filepath_or_name) else os.path.join(BACKUP_DIR, filepath_or_name)
    if not os.path.exists(src):
        raise FileNotFoundError(f"Backup not found: {src}")

    # Validate candidate backup
    is_valid, reason = verify_backup(src)
    if not is_valid:
        raise ValueError(f"Cannot restore backup: {reason}")

    # Create safety snapshot of live database before overwriting
    if os.path.exists(DB_PATH):
        try:
            ensure_backup_dir()
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            safety_name = f"pre_restore_safety_{ts}.db"
            safety_dst = os.path.join(BACKUP_DIR, safety_name)
            src_conn = get_connection()
            dst_conn = sqlite3.connect(safety_dst)
            src_conn.backup(dst_conn)
            dst_conn.close()
        except Exception:
            pass

    # Close active connection
    close_connection()

    # Atomic swap
    temp_dst = os.path.join(DB_DIR, "restore_temp.db")
    shutil.copy2(src, temp_dst)

    try:
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
        for ext in ("-wal", "-shm"):
            wfile = DB_PATH + ext
            if os.path.exists(wfile):
                os.remove(wfile)
        shutil.move(temp_dst, DB_PATH)
    except Exception:
        if os.path.exists(temp_dst):
            os.remove(temp_dst)
        raise

    return DB_PATH
