"""Admin commands.

uv run python -m backend.cli create-user client@example.com      # prints a password
uv run python -m backend.cli set-password client@example.com
uv run python -m backend.cli export-demo you@example.com demo.json
uv run python -m backend.cli seed-demo demo.json                  # replaces demo data
uv run python -m backend.cli access-requests
"""

import argparse
import json
import secrets
import sys
from pathlib import Path

from sqlmodel import SQLModel, col, select

from backend.auth import ensure_demo_user, hash_password
from backend.database import init_db, session_scope
from backend.models import (
    AccessRequest,
    Alert,
    Offer,
    PriceSnapshot,
    Product,
    Run,
    RunEvent,
    User,
)

TABLES: list[type[SQLModel]] = [Product, Offer, Run, RunEvent, PriceSnapshot, Alert]


def create_user(email: str, password: str | None) -> None:
    password = password or secrets.token_urlsafe(9)
    with session_scope() as session:
        if session.exec(select(User).where(User.email == email)).first():
            sys.exit(f"User {email} already exists (use set-password).")
        session.add(User(email=email, password_hash=hash_password(password)))
        session.commit()
    print(f"Created {email}\nPassword: {password}")


def set_password(email: str, password: str | None) -> None:
    password = password or secrets.token_urlsafe(9)
    with session_scope() as session:
        user = session.exec(select(User).where(User.email == email)).first()
        if user is None:
            sys.exit(f"No user {email}.")
        user.password_hash = hash_password(password)
        session.commit()
    print(f"New password for {email}: {password}")


def _rows(session, model, column, ids) -> list[dict]:
    rows = session.exec(select(model).where(col(column).in_(ids))).all()
    return [json.loads(r.model_dump_json()) for r in rows]


def export_workspace(email: str, path: Path) -> None:
    with session_scope() as session:
        user = session.exec(select(User).where(User.email == email)).first()
        if user is None:
            sys.exit(f"No user {email}.")
        products = _rows(session, Product, Product.user_id, [user.id])
        offers = _rows(session, Offer, Offer.product_id, [p["id"] for p in products])
        runs = _rows(session, Run, Run.user_id, [user.id])
        data = {
            "Product": products,
            "Offer": offers,
            "Run": runs,
            "RunEvent": _rows(session, RunEvent, RunEvent.run_id, [r["id"] for r in runs]),
            "PriceSnapshot": _rows(
                session, PriceSnapshot, PriceSnapshot.offer_id, [o["id"] for o in offers]
            ),
            "Alert": _rows(session, Alert, Alert.user_id, [user.id]),
        }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Exported {len(products)} products, {len(runs)} runs to {path}")


def seed_demo(path: Path) -> None:
    """Loads an exported workspace into the demo account (ids are re-mapped)."""
    data = json.loads(path.read_text(encoding="utf-8"))
    with session_scope() as session:
        demo = ensure_demo_user(session)
        # wipe the old demo data first
        old_products = [
            p.id for p in session.exec(select(Product).where(Product.user_id == demo.id))
        ]
        old_offers = [
            o.id for o in session.exec(select(Offer).where(col(Offer.product_id).in_(old_products)))
        ]
        old_runs = [r.id for r in session.exec(select(Run).where(Run.user_id == demo.id))]
        for model, column, ids in [
            (Alert, Alert.user_id, [demo.id]),
            (PriceSnapshot, PriceSnapshot.offer_id, old_offers),
            (RunEvent, RunEvent.run_id, old_runs),
            (Offer, Offer.id, old_offers),
            (Run, Run.id, old_runs),
            (Product, Product.id, old_products),
        ]:
            for row in session.exec(select(model).where(col(column).in_(ids))):
                session.delete(row)
            session.flush()

        id_maps: dict[str, dict[int, int]] = {name: {} for name in data}
        foreign = {"product_id": "Product", "offer_id": "Offer", "run_id": "Run"}
        for model in TABLES:
            name = model.__name__
            for row in data.get(name, []):
                old_id = row.pop("id")
                if "user_id" in row:
                    row["user_id"] = demo.id
                for key, target in foreign.items():
                    if row.get(key) is not None:
                        row[key] = id_maps[target].get(row[key])
                obj = model.model_validate(row)
                session.add(obj)
                session.flush()
                id_maps[name][old_id] = obj.id
        session.commit()
    print(f"Demo workspace loaded from {path}")


def list_access_requests() -> None:
    with session_scope() as session:
        for r in session.exec(select(AccessRequest).order_by(col(AccessRequest.created_at).desc())):
            print(
                f"{r.created_at:%Y-%m-%d %H:%M}  {r.name} <{r.email}>  {r.company or ''}\n"
                f"    {r.message}"
            )


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(prog="python -m backend.cli")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("create-user", "set-password"):
        cmd = sub.add_parser(name)
        cmd.add_argument("email")
        cmd.add_argument("--password")
    cmd = sub.add_parser("export-demo")
    cmd.add_argument("email")
    cmd.add_argument("path", type=Path)
    cmd = sub.add_parser("seed-demo")
    cmd.add_argument("path", type=Path)
    sub.add_parser("access-requests")
    args = parser.parse_args()

    init_db()
    match args.command:
        case "create-user":
            create_user(args.email, args.password)
        case "set-password":
            set_password(args.email, args.password)
        case "export-demo":
            export_workspace(args.email, args.path)
        case "seed-demo":
            seed_demo(args.path)
        case "access-requests":
            list_access_requests()


if __name__ == "__main__":
    main()
