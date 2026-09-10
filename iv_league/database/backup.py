import os
import shutil
import sqlite3
import datetime
from ..database.db import DB_PATH, _get_db_dir

BACKUP_DIR = os.path.join(_get_db_dir(), "backups")

def ensure_backup_dir():
    os.makedirs(BACKUP_DIR, exist_ok=True)

def create_backup(filename=None):
    ensure_backup_dir()
    if filename is None:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"iv_league_{timestamp}.db"
    src = DB_PATH
    dst = os.path.join(BACKUP_DIR, filename)
    if not os.path.exists(src):
        raise FileNotFoundError(f"Database not found: {src}")
    shutil.copy2(src, dst)
    return dst

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
    return False

def restore_backup(filename):
    src = os.path.join(BACKUP_DIR, filename)
    if not os.path.exists(src):
        raise FileNotFoundError(f"Backup not found: {src}")
    conn = sqlite3.connect(DB_PATH)
    conn.close()
    shutil.copy2(src, DB_PATH)
    return DB_PATH
