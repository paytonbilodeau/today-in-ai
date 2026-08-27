#!/usr/bin/env python3
"""Build and enforce the rolling seven-day Today in AI novelty review."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import date, timedelta
from pathlib import Path


WORKSPACE = Path("~/workspace").expanduser()
WINDOW_DAYS = 7
COPY_SIMILARITY_LIMIT = 0.52
WORD_RE = re.compile(r"[a-z0-9]+")
STOPWORDS = {
    "a",
    "about",
    "ai",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "but",
    "by",
    "can",
    "for",
    "from",
    "has",
    "have",
    "in",
    "is",
    "it",
    "its",
    "of",
    "on",
    "or",
    "that",
    "the",
    "their",
    "they",
    "this",
    "to",
    "was",
    "were",
    "while",
    "with",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalize(value: str) -> str:
    return " ".join(WORD_RE.findall(value.lower()))


def extract_story_headings(copy: str) -> list[str]:
    headings: list[str] = []
    paragraphs = [item.strip() for item in re.split(r"\n\s*\n", copy) if item.strip()]
    for paragraph in paragraphs[1:]:
        if "\n" in paragraph:
            continue
        stripped = paragraph.strip()
        words = stripped.rstrip(":").split()
        if (
            2 <= len(words) <= 8
            and not stripped.endswith((".", "?", "!"))
            and "http://" not in stripped
            and "https://" not in stripped
        ):
            headings.append(stripped.rstrip(":"))
    return headings


def extract_hook(package: str, prompt: str) -> str:
    for text in (package, prompt):
        match = re.search(r"(?:^|\n)-?\s*Hook:\s*`([^`]+)`", text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return ""


def extract_meme(package: str, prompt: str) -> str:
    combined = f"{package}\n{prompt}"
    known = (
        ("Awkward Look Monkey Puppet", "Awkward Look Monkey Puppet"),
        ("Two Buttons", "Two Buttons"),
        ("Drake Hotline Bling", "Drake Hotline Bling"),
        ("Drakeposting", "Drakeposting"),
    )
    for needle, label in known:
        if needle.lower() in combined.lower():
            return label
    match = re.search(
        r"(?:^|\n)-?\s*Meme reference:\s*([^\n]+)",
        combined,
        re.IGNORECASE,
    )
    if match:
        return match.group(1).strip()
    return ""


def meme_family(meme: str, visual_concept: str = "") -> str:
    value = normalize(f"{meme} {visual_concept}")
    if "drake" in value or (
        "two panel" in value and "reject" in value and "approv" in value
    ):
        return "two-panel reject/approve"
    if "two buttons" in value:
        return "two-button dilemma"
    if "awkward look monkey puppet" in value or "side eye" in value:
        return "guilty side-eye"
    return normalize(meme)


def extract_visual_concept(prompt: str) -> str:
    match = re.search(
        r"(?:^|\n)Primary request:\s*([^\n]+)",
        prompt,
        re.IGNORECASE,
    )
    return match.group(1).strip() if match else ""


def load_asset_manifest(edition_dir: Path) -> dict:
    path = edition_dir / "image-assets.json"
    if not path.is_file():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return value if isinstance(value, dict) else {}


def structured_visual_fields(manifest: dict) -> dict:
    source = manifest.get("visual_source")
    composition = manifest.get("composition")
    if not isinstance(source, dict):
        source = {}
    if not isinstance(composition, dict):
        composition = {}
    return {
        "visual_source_kind": str(source.get("kind", "")).strip(),
        "visual_source_name": str(source.get("name", "")).strip(),
        "meme_family": str(source.get("family", "")).strip(),
        "main_composition": str(composition.get("main_composition", "")).strip(),
        "subject_pose": str(composition.get("subject_pose", "")).strip(),
        "prop_setup": str(composition.get("prop_setup", "")).strip(),
        "visual_joke": str(composition.get("visual_joke", "")).strip(),
    }


def copy_tokens(copy: str) -> set[str]:
    return {token for token in WORD_RE.findall(copy.lower()) if token not in STOPWORDS}


def copy_similarity(left: str, right: str) -> float:
    left_tokens = copy_tokens(left)
    right_tokens = copy_tokens(right)
    union = left_tokens | right_tokens
    if not union:
        return 0.0
    return len(left_tokens & right_tokens) / len(union)


def edition_snapshot(workspace: Path, edition_date: date) -> dict | None:
    edition_dir = workspace / "today-in-ai" / "editions" / edition_date.isoformat()
    image_dir = workspace / "today-in-ai" / "images" / edition_date.isoformat()
    copy_path = edition_dir / "copy.txt"
    if not copy_path.is_file():
        return None

    package_path = edition_dir / "package.md"
    prompt_path = edition_dir / "image-prompt.txt"
    results_path = edition_dir / "publish-results.json"
    copy = copy_path.read_text(encoding="utf-8")
    package = package_path.read_text(encoding="utf-8") if package_path.is_file() else ""
    prompt = prompt_path.read_text(encoding="utf-8") if prompt_path.is_file() else ""
    results = {}
    if results_path.is_file():
        try:
            results = json.loads(results_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            results = {}
    images = sorted(image_dir.glob("*final.png"))
    image_path = images[0] if images else None
    meme = extract_meme(package, prompt)
    visual_concept = extract_visual_concept(prompt)
    asset_manifest = load_asset_manifest(edition_dir)
    structured = structured_visual_fields(asset_manifest)
    hook = str(asset_manifest.get("hook", "")).strip() or extract_hook(package, prompt)
    structured_family = structured["meme_family"]

    return {
        "date": edition_date.isoformat(),
        "status": results.get("status", "candidate"),
        "headings": extract_story_headings(copy),
        "hook": hook,
        "meme": structured["visual_source_name"] or meme,
        "meme_family": (
            normalize(structured_family)
            if structured_family
            else meme_family(meme, visual_concept)
        ),
        "visual_source_kind": structured["visual_source_kind"],
        "visual_concept": visual_concept,
        "main_composition": structured["main_composition"],
        "subject_pose": structured["subject_pose"],
        "prop_setup": structured["prop_setup"],
        "visual_joke": structured["visual_joke"],
        "copy_path": str(copy_path),
        "copy": copy,
        "image_path": str(image_path) if image_path else "",
        "image_sha256": sha256(image_path) if image_path else "",
    }


def compare_candidate(candidate: dict, recent: list[dict]) -> dict:
    failures: list[str] = []
    similarities: list[dict] = []
    candidate_headings = {normalize(item) for item in candidate["headings"]}

    for prior in recent:
        prior_headings = {normalize(item) for item in prior["headings"]}
        repeated_headings = sorted(candidate_headings & prior_headings)
        if repeated_headings:
            failures.append(
                f"{prior['date']}: repeated story heading: {', '.join(repeated_headings)}"
            )

        if candidate["hook"] and normalize(candidate["hook"]) == normalize(prior["hook"]):
            failures.append(f"{prior['date']}: repeated image hook: {candidate['hook']}")

        if (
            candidate["meme_family"]
            and candidate["meme_family"] == prior["meme_family"]
        ):
            failures.append(
                f"{prior['date']}: repeated meme family: {candidate['meme_family']}"
            )

        if (
            candidate["image_sha256"]
            and candidate["image_sha256"] == prior["image_sha256"]
        ):
            failures.append(f"{prior['date']}: identical final image file")

        for field, label in (
            ("main_composition", "main composition"),
            ("subject_pose", "subject pose"),
            ("prop_setup", "prop setup"),
            ("visual_joke", "visual joke"),
        ):
            candidate_value = normalize(candidate.get(field, ""))
            prior_value = normalize(prior.get(field, ""))
            if candidate_value and candidate_value == prior_value:
                failures.append(
                    f"{prior['date']}: repeated {label}: {candidate[field]}"
                )

        similarity = copy_similarity(candidate["copy"], prior["copy"])
        similarities.append({"date": prior["date"], "score": round(similarity, 3)})
        if similarity >= COPY_SIMILARITY_LIMIT:
            failures.append(
                f"{prior['date']}: copy similarity {similarity:.3f} exceeds "
                f"{COPY_SIMILARITY_LIMIT:.2f}"
            )

    return {
        "status": "pass" if not failures else "fail",
        "hard_failures": failures,
        "copy_similarity": similarities,
    }


def build_review(workspace: Path, run_date: date) -> dict:
    start = run_date - timedelta(days=WINDOW_DAYS)
    dates = [start + timedelta(days=offset) for offset in range(WINDOW_DAYS)]
    recent = [
        snapshot
        for item_date in dates
        if (snapshot := edition_snapshot(workspace, item_date)) is not None
    ]
    candidate = edition_snapshot(workspace, run_date)
    comparison = (
        compare_candidate(candidate, recent)
        if candidate
        else {
            "status": "pending",
            "hard_failures": [],
            "copy_similarity": [],
        }
    )
    return {
        "run_date": run_date.isoformat(),
        "window_start": start.isoformat(),
        "window_end": (run_date - timedelta(days=1)).isoformat(),
        "window_days": WINDOW_DAYS,
        "recent_editions": recent,
        "candidate": candidate,
        "comparison": comparison,
    }


def markdown_escape(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def render_markdown(review: dict) -> str:
    lines = [
        f"# Today in AI Recent Seven-Day Review: {review['run_date']}",
        "",
        (
            f"Comparison window: {review['window_start']} through "
            f"{review['window_end']}. This is the only historical window used."
        ),
        "",
        "## Recent Editions",
        "",
        "| Date | Story headings | Hook | Visual source | Meme family | Main composition | Final image |",
        "|---|---|---|---|---|---|---|",
    ]
    if review["recent_editions"]:
        for item in review["recent_editions"]:
            image = (
                f"[open](<{item['image_path']}>)" if item["image_path"] else "missing"
            )
            lines.append(
                "| "
                + " | ".join(
                    (
                        item["date"],
                        markdown_escape("; ".join(item["headings"]) or "missing"),
                        markdown_escape(item["hook"] or "missing"),
                        markdown_escape(item["visual_source_kind"] or "legacy"),
                        markdown_escape(item["meme_family"] or item["meme"] or "missing"),
                        markdown_escape(item["main_composition"] or "legacy prompt"),
                        image,
                    )
                )
                + " |"
            )
    else:
        lines.append("| None found |  |  |  |  |  |  |")

    lines.extend(["", "## Candidate Machine Check", ""])
    candidate = review["candidate"]
    if not candidate:
        lines.append("Candidate files do not exist yet. Run this check again after drafting.")
    else:
        comparison = review["comparison"]
        lines.extend(
            [
                f"- Result: `{comparison['status'].upper()}`",
                f"- Story headings: {', '.join(candidate['headings']) or 'missing'}",
                f"- Hook: `{candidate['hook'] or 'missing'}`",
                f"- Meme family: `{candidate['meme_family'] or 'missing'}`",
                (
                    "- Main composition: "
                    f"`{candidate['main_composition'] or 'missing structured field'}`"
                ),
                (
                    "- Subject pose: "
                    f"`{candidate['subject_pose'] or 'missing structured field'}`"
                ),
                (
                    "- Prop setup: "
                    f"`{candidate['prop_setup'] or 'missing structured field'}`"
                ),
                (
                    "- Visual joke: "
                    f"`{candidate['visual_joke'] or 'missing structured field'}`"
                ),
            ]
        )
        if comparison["copy_similarity"]:
            similarities = ", ".join(
                f"{item['date']}={item['score']:.3f}"
                for item in comparison["copy_similarity"]
            )
            lines.append(f"- Copy similarity: {similarities}")
        if comparison["hard_failures"]:
            lines.append("- Blocking findings:")
            lines.extend(f"  - {item}" for item in comparison["hard_failures"])
        else:
            lines.append("- Blocking findings: none")

    lines.extend(
        [
            "",
            "## Required Human Visual Check",
            "",
            "Open each listed final image, then compare the candidate at full size and phone size.",
            "Reject the candidate if it repeats a meme mechanic, main composition, subject pose, prop setup, dominant visual joke, or substantially similar hook from this window.",
            "Also reject a repeated story unless a meaningful new event occurred and the copy states exactly what changed.",
            "",
            "Record the final visual and editorial judgment in the dated `package.md` before publishing.",
            "",
        ]
    )
    return "\n".join(lines)


def write_review(workspace: Path, review: dict) -> Path:
    destination = (
        workspace
        / "today-in-ai"
        / "editions"
        / review["run_date"]
        / "recent-seven-review.md"
    )
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_markdown(review), encoding="utf-8")
    return destination


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True, help="Candidate date in YYYY-MM-DD")
    parser.add_argument("--workspace", type=Path, default=WORKSPACE)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    run_date = date.fromisoformat(args.date)
    review = build_review(args.workspace, run_date)
    report_path = write_review(args.workspace, review) if args.write else None
    output = {
        "run_date": review["run_date"],
        "window_start": review["window_start"],
        "window_end": review["window_end"],
        "recent_count": len(review["recent_editions"]),
        "candidate_present": review["candidate"] is not None,
        "status": review["comparison"]["status"],
        "hard_failures": review["comparison"]["hard_failures"],
        "report": str(report_path) if report_path else None,
    }
    print(json.dumps(output, indent=2))

    if args.check:
        if review["candidate"] is None:
            print("candidate files are missing", flush=True)
            return 1
        if review["comparison"]["hard_failures"]:
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
