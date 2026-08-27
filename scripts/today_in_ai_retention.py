#!/usr/bin/env python3
"""Move old Today in AI Desktop delivery copies to Trash every 14 days."""

from __future__ import annotations

import argparse
import json
import re
import shutil
from datetime import date, datetime, timedelta
from pathlib import Path


DEFAULT_DELIVERY_ROOT = Path("/Users/paytonbilodeau/Desktop/Leverage/Today in AI")
DEFAULT_STATE_FILE = Path(
    "/Users/paytonbilodeau/Documents/Business Vibe Coding/"
    "today-in-ai/retention-state.json"
)
DEFAULT_TRASH_ROOT = Path.home() / ".Trash"
FOLDER_RE = re.compile(r"^Today in AI - (\d{4}-\d{2}-\d{2})$")
KEEP_DAYS = 7
CLEANUP_INTERVAL_DAYS = 14


def load_state(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def cleanup_due(run_date: date, state: dict) -> bool:
    value = state.get("last_cleanup_date")
    if not value:
        return True
    try:
        previous = date.fromisoformat(value)
    except ValueError:
        return True
    return (run_date - previous).days >= CLEANUP_INTERVAL_DAYS


def retention_plan(delivery_root: Path, run_date: date) -> dict:
    cutoff = run_date - timedelta(days=KEEP_DAYS - 1)
    keep: list[str] = []
    trash: list[str] = []
    ignored: list[str] = []
    if delivery_root.is_dir():
        for path in sorted(delivery_root.iterdir()):
            if not path.is_dir():
                ignored.append(str(path))
                continue
            match = FOLDER_RE.fullmatch(path.name)
            if not match:
                ignored.append(str(path))
                continue
            folder_date = date.fromisoformat(match.group(1))
            if folder_date < cutoff:
                trash.append(str(path))
            else:
                keep.append(str(path))
    return {
        "run_date": run_date.isoformat(),
        "keep_days": KEEP_DAYS,
        "keep_from": cutoff.isoformat(),
        "keep": keep,
        "trash": trash,
        "ignored": ignored,
    }


def unique_trash_destination(trash_root: Path, source: Path) -> Path:
    destination = trash_root / source.name
    if not destination.exists():
        return destination
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return trash_root / f"{source.name} cleanup {stamp}"


def apply_retention(plan: dict, trash_root: Path) -> list[dict]:
    trash_root.mkdir(parents=True, exist_ok=True)
    moved: list[dict] = []
    for raw_source in plan["trash"]:
        source = Path(raw_source)
        destination = unique_trash_destination(trash_root, source)
        shutil.move(str(source), str(destination))
        moved.append({"source": str(source), "trash": str(destination)})
    return moved


def write_state(path: Path, run_date: date, moved: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    state = {
        "last_cleanup_date": run_date.isoformat(),
        "cleanup_interval_days": CLEANUP_INTERVAL_DAYS,
        "desktop_keep_days": KEEP_DAYS,
        "last_moved": moved,
        "note": (
            "Only dated Desktop delivery copies are moved to Trash. "
            "Workspace editions, images, logs, manifests, and receipts are retained."
        ),
    }
    path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True, help="Run date in YYYY-MM-DD")
    parser.add_argument("--delivery-root", type=Path, default=DEFAULT_DELIVERY_ROOT)
    parser.add_argument("--state-file", type=Path, default=DEFAULT_STATE_FILE)
    parser.add_argument("--trash-root", type=Path, default=DEFAULT_TRASH_ROOT)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    run_date = date.fromisoformat(args.date)
    state = load_state(args.state_file)
    due = cleanup_due(run_date, state)
    plan = retention_plan(args.delivery_root, run_date)
    moved: list[dict] = []

    if args.apply and due:
        moved = apply_retention(plan, args.trash_root)
        write_state(args.state_file, run_date, moved)

    if args.apply and due:
        status = "applied"
        next_due_on = (run_date + timedelta(days=CLEANUP_INTERVAL_DAYS)).isoformat()
    elif args.apply:
        status = "not_due"
        last_cleanup = date.fromisoformat(state["last_cleanup_date"])
        next_due_on = (
            last_cleanup + timedelta(days=CLEANUP_INTERVAL_DAYS)
        ).isoformat()
    else:
        status = "dry_run"
        next_due_on = None

    print(
        json.dumps(
            {
                "status": status,
                "due": due,
                "next_due_on": next_due_on,
                "plan": plan,
                "moved": moved,
                "safety": (
                    "Only exact Today in AI - YYYY-MM-DD directories under the "
                    "Desktop delivery root are eligible."
                ),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
