"""Management commands for first run / ops.

Usage:
    python -m app.cli initdb
    python -m app.cli createuser <username> <password> [display_name]
    python -m app.cli syncparcels

These are thin wrappers so an operator can set up the database and team accounts
without writing code. Run from the ``backend/`` directory with the venv active
(or via ``docker compose exec backend python -m app.cli ...``).
"""
from __future__ import annotations

import sys


def _initdb() -> None:
    from app.database import init_db

    init_db()
    print("✅ Database initialized (PostGIS extension + application tables).")


def _createuser(username: str, password: str, display_name: str | None = None) -> None:
    from app.auth import hash_password
    from app.database import SessionLocal
    from app.models import User

    db = SessionLocal()
    try:
        if db.query(User).filter(User.username == username).first():
            print(f"⚠️  User {username!r} already exists.")
            return
        db.add(
            User(
                username=username,
                password_hash=hash_password(password),
                display_name=display_name,
            )
        )
        db.commit()
        print(f"✅ Created user {username!r}.")
    finally:
        db.close()


def _syncparcels() -> None:
    from app.gis.county_sync import COUNTY_SOURCES, sync_county

    for key in COUNTY_SOURCES:
        outcome = sync_county(key)
        print(f"  {key}: {outcome.status}"
              + (f" ({outcome.parcel_count} parcels)" if outcome.parcel_count else ""))


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    if not argv:
        print(__doc__)
        return 1
    cmd, *rest = argv
    if cmd == "initdb":
        _initdb()
    elif cmd == "createuser":
        if len(rest) < 2:
            print("usage: python -m app.cli createuser <username> <password> [display_name]")
            return 1
        _createuser(rest[0], rest[1], rest[2] if len(rest) > 2 else None)
    elif cmd == "syncparcels":
        _syncparcels()
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
