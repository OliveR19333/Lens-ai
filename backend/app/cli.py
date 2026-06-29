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


def _importparcels(args: list[str]) -> None:
    from app.config import get_settings
    from app.gis import shapefile_import as shp

    if not args:
        print("usage: python -m app.cli importparcels <county> <zip_path> [--list] [--layer NAME]")
        return
    county = args[0]
    zip_path = args[1] if len(args) > 1 else None
    if "--list" in args or not zip_path:
        if not zip_path:
            print("Provide the path to the zip: importparcels <county> <zip_path> --list")
            return
        print(f"Layers in {zip_path}:")
        for li in shp.list_layers(zip_path):
            print(f"  [{li.score:>2}]  {li.name:<28} {li.n_features:>8} features  fields={li.fields[:6]}")
        print("\nThe top-scored layer is used by default; override with --layer NAME.")
        return
    layer = None
    if "--layer" in args:
        i = args.index("--layer")
        layer = args[i + 1] if i + 1 < len(args) else None
    summary = shp.import_parcels(county, zip_path, get_settings().data_dir, layer=layer)
    print(
        f"✅ Imported {summary['parcels']} parcels for {summary['county']} "
        f"from layer '{summary['layer']}' ({summary['bundle_kb']} KB bundle, v{summary['version']})."
    )


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
    elif cmd == "importparcels":
        _importparcels(rest)
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
