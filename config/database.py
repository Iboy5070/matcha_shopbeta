"""Database config — PostgreSQL in production, SQLite fallback for local dev."""

from __future__ import annotations

import os
import socket
import sys
from pathlib import Path
from urllib.parse import urlparse

import dj_database_url


def _sqlite_path(base_dir: Path) -> str:
    return f"sqlite:///{base_dir / 'db.sqlite3'}"


def _postgres_reachable(db_url: str, timeout: float = 0.5) -> bool:
    try:
        parsed = urlparse(db_url)
        host = parsed.hostname or "127.0.0.1"
        port = parsed.port or 5432
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def configure_databases(base_dir: Path, debug: bool) -> dict:
    use_sqlite = os.getenv("USE_SQLITE", "").strip() == "1"
    sqlite_url = _sqlite_path(base_dir)
    db_url = (os.getenv("DATABASE_URL") or "").strip()

    if use_sqlite or not db_url:
        db_url = sqlite_url

    if (
        debug
        and not use_sqlite
        and db_url.startswith(("postgres://", "postgresql://"))
        and not _postgres_reachable(db_url)
    ):
        print(
            "\n⚠️  PostgreSQL ບໍ່ເປີດ — ໃຊ້ SQLite (db.sqlite3) ແທນ\n"
            "   ເປີດ Postgres: docker compose up -d db\n"
            "   ຫຼື ຕັ້ງ USE_SQLITE=1 ໃນ .env ເພື່ອໃຊ້ SQLite ຕະຫຼອດ\n",
            file=sys.stderr,
        )
        db_url = sqlite_url

    if db_url.startswith(("postgres://", "postgresql://")):
        cfg = dj_database_url.parse(db_url)
        cfg["CONN_MAX_AGE"] = 600
        cfg["CONN_HEALTH_CHECKS"] = True
    else:
        cfg = dj_database_url.parse(db_url)

    return {"default": cfg}
