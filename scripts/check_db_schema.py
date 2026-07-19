#!/usr/bin/env python3
"""Compare live PostgreSQL (Supabase) schema vs Django models.

Usage:
  DATABASE_URL=postgres://... python scripts/check_db_schema.py

Or set DATABASE_URL in .env and run:
  python scripts/check_db_schema.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django

django.setup()

from django.apps import apps
from django.db import connection


def django_tables() -> dict[str, set[str]]:
    skip = ("django_", "auth_", "admin_", "contenttypes_", "sessions_")
    out: dict[str, set[str]] = {}
    for model in apps.get_models():
        t = model._meta.db_table
        if any(t.startswith(p) for p in skip):
            continue
        out[t] = {f.column for f in model._meta.local_fields}
    return out


def pg_tables() -> dict[str, set[str]]:
    if connection.vendor != "postgresql":
        print(f"ERROR: connected to {connection.vendor}, need PostgreSQL (Supabase).")
        print("Set DATABASE_URL to your Supabase connection string.")
        sys.exit(1)

    with connection.cursor() as c:
        c.execute(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
            ORDER BY table_name
            """
        )
        tables = [r[0] for r in c.fetchall()]

        out: dict[str, set[str]] = {}
        for t in tables:
            if t.startswith(("django_", "auth_", "admin_", "contenttypes_", "sessions_")):
                continue
            c.execute(
                """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_schema = 'public' AND table_name = %s
                ORDER BY ordinal_position
                """,
                [t],
            )
            out[t] = {r[0] for r in c.fetchall()}
        return out


def main() -> None:
    expected = django_tables()
    actual = pg_tables()

    print("=== SUPABASE / POSTGRES (app tables) ===\n")
    for t in sorted(actual):
        print(f"{t} ({len(actual[t])} cols)")
        for col in sorted(actual[t]):
            print(f"  - {col}")
        print()

    print("=== COMPARE: Django vs DB ===\n")
    all_tables = sorted(set(expected) | set(actual))
    issues = 0
    for t in all_tables:
        exp = expected.get(t, set())
        act = actual.get(t, set())
        if t not in actual:
            print(f"MISSING TABLE in DB: {t}")
            issues += 1
            continue
        if t not in expected:
            print(f"EXTRA TABLE in DB (not in Django): {t}")
            issues += 1
            continue
        missing = exp - act
        extra = act - exp
        if missing:
            print(f"{t}: missing columns in DB → {sorted(missing)}")
            issues += 1
        if extra:
            print(f"{t}: extra columns in DB → {sorted(extra)}")
            issues += 1

    if issues == 0:
        print("OK — app tables match Django models.")
    else:
        print(f"\n{issues} issue(s). Fix: python manage.py migrate --noinput")
        print("Do NOT rename/drop columns in Supabase UI — change models.py + migrate instead.")


if __name__ == "__main__":
    main()
