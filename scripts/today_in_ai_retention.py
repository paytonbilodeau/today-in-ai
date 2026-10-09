#!/usr/bin/env python3
"""Retired age-only cleanup entry point; preserve files for exact-plan review."""

from __future__ import annotations

import argparse
import json
import re
from datetime import date, datetime, timedelta
from pathlib import Path


DEFAULT_DELIVERY_ROOT = Path("~/Desktop/Today in AI").expanduser()
DEFAULT_STATE_FILE = Path(
    "~/workspace/"
    "today-in-ai/retention-state.json"
).expanduser()
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
    raise RuntimeError("Age-only cleanup is retired. Use an exact reviewed file plan with verified retained copies.")


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

    date.fromisoformat(args.date)  # Preserve the historical date argument contract.
    print(json.dumps({
        "status": "retired_age_only_cleanup",
        "moved": [],
        "note": "No files or state were changed. After verified completion, use a separately authorized exact-file plan with retained copies, hashes and restore paths. See docs/retention.md."
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
