import os
import shutil
import sqlite3
import datetime
import hashlib
from ..database.db import DB_PATH, DB_DIR

BACKUP_DIR = os.path.join(DB_DIR, "backups")


def ensure_backup_dir():
    os.makedirs(BACKUP_DIR, exist_ok=True)


def _compute_sha256(filepath):
    """Compute SHA-256 checksum of a file."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()


def create_backup(filename=None):
    ensure_backup_dir()
    if filename is None:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"iv_league_{timestamp}.db"
    src = DB_PATH
    dst = os.path.join(BACKUP_DIR, filename)
    if not os.path.exists(src):
        raise FileNotFoundError(f"Database not found: {src}")
    
    # Compute checksum before copy for integrity verification
    checksum = _compute_sha256(src)
    
    shutil.copy2(src, dst)
    
    # Write checksum file alongside backup
    checksum_file = dst + ".sha256"
    with open(checksum_file, "w") as f:
        f.write(checksum)
    
    return dst


def list_backups():
    ensure_backup_dir()
    files = []
    for f in os.listdir(BACKUP_DIR):
        if f.lower().endswith(".db") and not f.endswith(".sha256"):
            p = os.path.join(BACKUP_DIR, f)
            files.append((f, os.path.getmtime(p), os.path.getsize(p)))
    files.sort(key=lambda x: x[1], reverse=True)
    return files


def delete_backup(filename):
    p = os.path.join(BACKUP_DIR, filename)
    if os.path.exists(p):
        os.remove(p)
    # Also remove checksum file if it exists
    checksum_file = p + ".sha256"
    if os.path.exists(checksum_file):
        os.remove(checksum_file)
    return True


def verify_backup(filename):
    """Verify the integrity of a backup file using its SHA-256 checksum."""
    p = os.path.join(BACKUP_DIR, filename)
    checksum_file = p + ".sha256"
    if not os.path.exists(checksum_file):
        return False
    with open(checksum_file, "r") as f:
        expected_checksum = f.read().strip()
    actual_checksum = _compute_sha256(p)
    return actual_checksum == expected_checksum


def restore_backup(filename):
    """Restore a backup with integrity verification and safe file operations."""
    src = os.path.join(BACKUP_DIR, filename)
    if not os.path.exists(src):
        raise FileNotFoundError(f"Backup not found: {src}")
    
    # Verify backup integrity before restoring
    if not verify_backup(filename):
        raise ValueError(
            f"Backup integrity check failed for {filename}. "
            "The backup file may be corrupted."
        )
    
    # Close any existing connections to ensure no locks
    from ..database.db import close_connection
    close_connection()
    
    # Use atomic rename: copy to temp, then rename over the live DB
    temp_dst = src + ".restoring"
    shutil.copy2(src, temp_dst)
    
    try:
        # Remove existing DB if it exists
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
        
        # Also remove WAL and SHM files if they exist
        for ext in ("-wal", "-shm"):
            wal_file = DB_PATH + ext
            if os.path.exists(wal_file):
                os.remove(wal_file)
        
        # Move temp file to final location (atomic on same filesystem)
        shutil.move(temp_dst, DB_PATH)
    except Exception:
        # Clean up temp file on failure
        if os.path.exists(temp_dst):
            os.remove(temp_dst)
        raise
    
    return DB_PATH
