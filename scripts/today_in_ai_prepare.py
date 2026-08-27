#!/usr/bin/env python3
"""Validate and package a finished Today in AI edition for Postiz."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
from datetime import date
from pathlib import Path

try:
    from today_in_ai_assets import AssetManifestError, validate_asset_manifest
    from today_in_ai_novelty import build_review, write_review
except ModuleNotFoundError:
    from execution.today_in_ai_assets import AssetManifestError, validate_asset_manifest
    from execution.today_in_ai_novelty import build_review, write_review


WORKSPACE = Path("~/workspace").expanduser()
DEFAULT_DELIVERY_ROOT = Path("~/Desktop/Today in AI").expanduser()
ASSET_MANIFEST_REQUIRED_FROM = date(2026, 7, 29)
ADAPTIVE_EDITORIAL_REQUIRED_FROM = date(2026, 8, 7)
LINK_FREE_PUBLIC_COPY_REQUIRED_FROM = date(2026, 8, 25)
FAKE_BOLD = re.compile(r"[\U0001D400-\U0001D7FF]")
URL_RE = re.compile(r"https://[^\s)>]+")
SOURCES_FOOTER_RE = re.compile(r"(?mi)^sources:\s*$")
WORD_RE = re.compile(r"\b[\w’'-]+\b")
BANNED = (
    "—",
    "–",
    "**",
    "delve",
    "leverage",
    "robust",
    "streamline",
    "harness",
    "elevate",
    "this changes everything",
    "here's the thing",
    "game-changer",
    "let's dive in",
    "what nobody tells you",
    "the uncomfortable truth is",
    "at the end of the day",
    "in today's world",
    "in conclusion",
    "this matters",
    "that matters",
    "why it matters",
    "what matters is",
    "this is important",
    "only time will tell",
    "welcome to the future",
    "we're just getting started",
    "one thing is clear",
    "buckle up",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def image_dimensions(path: Path) -> tuple[int, int]:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=width,height",
            "-of",
            "json",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    stream = json.loads(result.stdout)["streams"][0]
    return int(stream["width"]), int(stream["height"])


def parse_stories(copy: str) -> list[tuple[str, str]]:
    lines = copy.splitlines()[1:]
    stories: list[tuple[str, str]] = []
    heading = ""
    body_lines: list[str] = []
    for raw_line in lines:
        line = raw_line.strip()
        heading_words = WORD_RE.findall(line.rstrip(":"))
        is_heading = (
            line.endswith(":")
            and 3 <= len(heading_words) <= 7
            and not URL_RE.search(line)
        )
        if is_heading:
            if heading:
                stories.append((heading, "\n".join(body_lines).strip()))
            heading = line
            body_lines = []
        elif heading:
            body_lines.append(raw_line)
    if heading:
        stories.append((heading, "\n".join(body_lines).strip()))
    return stories


def validate_spaced_blocks(copy: str) -> None:
    """Require a real blank line between every title, heading, and body paragraph."""
    lines = copy.splitlines()
    for index in range(len(lines) - 1):
        if lines[index].strip() and lines[index + 1].strip():
            raise SystemExit(
                "copy needs a blank line between every title, heading, and body paragraph"
            )
    for heading, body in parse_stories(copy):
        paragraphs = [line.strip() for line in body.splitlines() if line.strip()]
        if len(paragraphs) < 2:
            raise SystemExit(
                f"story {heading} needs at least two spaced body paragraphs"
            )


def validate_copy(copy: str, run_date: date) -> dict:
    expected_title = f"Today in AI: {run_date.strftime('%B')} {run_date.day}"
    lines = copy.splitlines()
    if not lines or lines[0] != expected_title:
        raise SystemExit(f"first line must be exactly: {expected_title}")
    if FAKE_BOLD.search(copy):
        raise SystemExit("copy contains Unicode lookalike bold characters")
    if run_date >= LINK_FREE_PUBLIC_COPY_REQUIRED_FROM and (
        URL_RE.search(copy) or SOURCES_FOOTER_RE.search(copy)
    ):
        raise SystemExit(
            "public copy must not contain URLs or a Sources footer; keep research links in sources.md"
        )
    lowered = copy.lower()
    for item in BANNED:
        if item.lower() in lowered:
            raise SystemExit(f"copy contains banned text: {item}")
    stories = parse_stories(copy)
    if run_date >= ADAPTIVE_EDITORIAL_REQUIRED_FROM:
        if not 1 <= len(stories) <= 4:
            raise SystemExit(f"expected 1 to 4 story headings, found {len(stories)}")
        validate_spaced_blocks(copy)
    elif len(stories) not in (3, 4):
        raise SystemExit(f"expected 3 or 4 story headings, found {len(stories)}")
    for heading, body in stories:
        if not body:
            raise SystemExit(f"story body is empty: {heading}")
    if run_date >= ADAPTIVE_EDITORIAL_REQUIRED_FROM:
        story_words = [len(WORD_RE.findall(body)) for _, body in stories]
        ranges_by_count = {
            1: [(150, 360)],
            2: [(90, 210), (60, 180)],
            3: [(70, 170), (45, 130), (45, 130)],
            4: [(65, 150), (35, 105), (35, 105), (35, 105)],
        }
        for (heading, _), body_words, (minimum, maximum) in zip(
            stories, story_words, ranges_by_count[len(stories)]
        ):
            if not minimum <= body_words <= maximum:
                raise SystemExit(
                    f"story {heading} has {body_words} words; expected {minimum} to {maximum} "
                    f"for a {len(stories)}-story edition"
                )
    elif run_date >= ASSET_MANIFEST_REQUIRED_FROM:
        lead_words = len(WORD_RE.findall(stories[0][1]))
        if not 80 <= lead_words <= 130:
            raise SystemExit(
                f"lead story has {lead_words} words; expected 80 to 130"
            )
        for heading, body in stories[1:]:
            body_words = len(WORD_RE.findall(body))
            if not 35 <= body_words <= 60:
                raise SystemExit(
                    f"story {heading} has {body_words} words; expected 35 to 60"
                )
    words = len(WORD_RE.findall(copy))
    minimum_words = 160 if run_date >= ADAPTIVE_EDITORIAL_REQUIRED_FROM else 220
    if not minimum_words <= words <= 450:
        raise SystemExit(
            f"copy word count {words} is outside {minimum_words} to 450"
        )
    return {
        "words": words,
        "story_count": len(stories),
        "story_words": [len(WORD_RE.findall(body)) for _, body in stories],
    }


def validate_sources(sources: str) -> dict:
    urls = URL_RE.findall(sources)
    unique_urls = list(dict.fromkeys(urls))
    if len(unique_urls) < 3:
        raise SystemExit(
            f"sources.md must contain at least three https source URLs, found {len(unique_urls)}"
        )
    return {"source_url_count": len(unique_urls)}


def manifest(copy: str, image: Path, target: str) -> dict:
    target_payload: dict[str, object] = {
        "enabled": True,
        "method": "postiz",
        "caption": copy,
    }
    if target == "x":
        target_payload["who_can_reply"] = "everyone"
    return {
        "schema_version": 1,
        "workflow": "image",
        "quality": {
            "mode": "highest_supported",
            "preserve_source": True,
            "allow_upscale": False,
        },
        "publish_at": None,
        "media": {
            "video": None,
            "thumbnail": None,
            "images": [str(image)],
        },
        "disclosures": {
            "ai_generated": True,
            "paid_promotion": False,
            "made_for_kids": False,
        },
        "targets": {target: target_payload},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True, help="Edition date in YYYY-MM-DD")
    parser.add_argument("--workspace", type=Path, default=WORKSPACE)
    parser.add_argument("--outputs-root", type=Path)
    parser.add_argument("--delivery-root", type=Path, default=DEFAULT_DELIVERY_ROOT)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate all local gates without writing delivery files or manifests",
    )
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    run_date = date.fromisoformat(args.date)
    workspace = args.workspace.resolve()
    outputs_root = (
        args.outputs_root.resolve()
        if args.outputs_root
        else workspace / "outputs" / "social-publisher"
    )
    edition_dir = workspace / "today-in-ai" / "editions" / args.date
    image_dir = workspace / "today-in-ai" / "images" / args.date
    copy_path = edition_dir / "copy.txt"
    sources_path = edition_dir / "sources.md"
    prompt_path = edition_dir / "image-prompt.txt"
    package_path = edition_dir / "package.md"
    asset_manifest_path = edition_dir / "image-assets.json"
    image_path = image_dir / f"today-in-ai-{run_date.strftime('%B').lower()}-{run_date.day}-final.png"

    for required in (copy_path, sources_path, prompt_path, image_path):
        if not required.is_file():
            raise SystemExit(f"missing required edition file: {required}")
    if (
        run_date >= ASSET_MANIFEST_REQUIRED_FROM
        and not asset_manifest_path.is_file()
    ):
        raise SystemExit(f"missing required edition file: {asset_manifest_path}")

    copy = copy_path.read_text(encoding="utf-8").rstrip() + "\n"
    copy_result = validate_copy(copy, run_date)
    sources_result = validate_sources(sources_path.read_text(encoding="utf-8"))
    asset_result = None
    if asset_manifest_path.is_file():
        try:
            asset_result = validate_asset_manifest(
                asset_manifest_path,
                workspace=workspace,
                prompt_path=prompt_path,
            )
        except AssetManifestError as exc:
            raise SystemExit(f"image asset manifest failed: {exc}") from exc
    novelty_review = build_review(workspace, run_date)
    novelty_path = (
        edition_dir / "recent-seven-review.md"
        if args.dry_run
        else write_review(workspace, novelty_review)
    )
    novelty_failures = novelty_review["comparison"]["hard_failures"]
    if novelty_failures:
        joined = "\n- ".join(novelty_failures)
        raise SystemExit(f"rolling seven-day novelty gate failed:\n- {joined}")
    dimensions = image_dimensions(image_path)
    if dimensions != (1920, 1080):
        raise SystemExit(f"final image must be 1920x1080, got {dimensions[0]}x{dimensions[1]}")

    delivery = args.delivery_root / f"Today in AI - {args.date}"
    if args.dry_run:
        manifest_previews = {}
        for target in ("linkedin", "x"):
            preview = manifest(copy, image_path, target)
            target_payload = preview["targets"][target]
            manifest_previews[target] = {
                "workflow": preview["workflow"],
                "method": target_payload["method"],
                "caption_matches_copy": target_payload["caption"] == copy,
                "image": preview["media"]["images"][0],
                "quality_mode": preview["quality"]["mode"],
            }
        print(
            json.dumps(
                {
                    "status": "validated",
                    "dry_run": True,
                    "date": args.date,
                    "copy": copy_result,
                    "sources": sources_result,
                    "assets": asset_result,
                    "image": str(image_path),
                    "image_dimensions": list(dimensions),
                    "image_sha256": sha256(image_path),
                    "novelty_status": novelty_review["comparison"]["status"],
                    "delivery_would_be": str(delivery),
                    "manifest_previews": manifest_previews,
                },
                indent=2,
            )
        )
        return 0

    delivery.mkdir(parents=True, exist_ok=True)
    delivery_image = delivery / f"Today in AI - {args.date}.png"
    shutil.copy2(image_path, delivery_image)
    shutil.copy2(copy_path, delivery / f"Today in AI - {args.date}.txt")
    shutil.copy2(sources_path, delivery / "sources.md")
    shutil.copy2(prompt_path, delivery / "image-prompt.txt")
    shutil.copy2(novelty_path, delivery / "recent-seven-review.md")
    if package_path.is_file():
        shutil.copy2(package_path, delivery / "package.md")
    if asset_manifest_path.is_file():
        shutil.copy2(asset_manifest_path, delivery / "image-assets.json")

    outputs_root.mkdir(parents=True, exist_ok=True)
    created: list[Path] = []
    for target in ("linkedin", "x"):
        destination = outputs_root / f"today-in-ai-{args.date}-{target}.json"
        if destination.exists() and not args.force:
            raise SystemExit(f"refusing to overwrite existing manifest: {destination}")
        destination.write_text(
            json.dumps(manifest(copy, delivery_image, target), indent=2, ensure_ascii=False)
            + "\n",
            encoding="utf-8",
        )
        created.append(destination)

    if sha256(image_path) != sha256(delivery_image):
        raise SystemExit("delivery image does not match workspace final")

    print(
        json.dumps(
            {
                "status": "ready",
                "date": args.date,
                "copy_words": copy_result["words"],
                "story_words": copy_result["story_words"],
                "source_url_count": sources_result["source_url_count"],
                "asset_manifest_status": (
                    asset_result["status"] if asset_result else "legacy"
                ),
                "image": str(image_path),
                "image_sha256": sha256(image_path),
                "novelty_review": str(novelty_path),
                "novelty_status": novelty_review["comparison"]["status"],
                "delivery": str(delivery),
                "manifests": [str(path) for path in created],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
