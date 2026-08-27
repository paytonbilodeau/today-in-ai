#!/usr/bin/env python3
"""Build the durable Fireship reference corpus used by Today in AI.

The script uses the local yt-dlp binary to collect the public channel catalog,
select a balanced study set, download thumbnails and English subtitles, and
create clean reading copies. Raw VTT files remain untouched. Closing sponsor
segments are removed only from the derived editorial copies.
"""

from __future__ import annotations

import argparse
import csv
import html
import json
import re
import shutil
import subprocess
import sys
import tempfile
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path


WORKSPACE = Path("/Users/paytonbilodeau/Documents/Business Vibe Coding")
DEFAULT_OUTPUT = WORKSPACE / "youtube" / "fireship-today-in-ai-library" / "data"
DEFAULT_CHANNEL = "https://www.youtube.com/@Fireship"
TAG_RE = re.compile(r"<[^>]+>")
TIMESTAMP_RE = re.compile(
    r"^(?:\d{2}:)?\d{2}:\d{2}\.\d{3}\s+-->\s+(?:\d{2}:)?\d{2}:\d{2}\.\d{3}"
)
WORD_RE = re.compile(r"[\w’'-]+")
SPONSOR_RE = re.compile(
    r"\b(?:today(?:'s| is)? video is sponsored by|sponsored by|thanks to .{0,45} "
    r"for sponsoring|thanks to .{0,140} sponsoring|a quick word from|our sponsor|"
    r"this video was brought to you by)\b",
    re.IGNORECASE,
)
URL_HOST_RE = re.compile(r"https?://(?:www\.)?([^/\s]+)", re.IGNORECASE)


def run(command: list[str], *, capture: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        check=True,
        capture_output=capture,
        text=True,
    )


def clean_caption_text(text: str) -> str:
    text = html.unescape(TAG_RE.sub("", text))
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _append_with_overlap(words: list[str], cue_words: list[str]) -> None:
    if not cue_words:
        return
    maximum = min(len(words), len(cue_words), 80)
    overlap = 0
    for size in range(maximum, 0, -1):
        if [w.casefold() for w in words[-size:]] == [
            w.casefold() for w in cue_words[:size]
        ]:
            overlap = size
            break
    words.extend(cue_words[overlap:])


def vtt_to_text(vtt: str) -> str:
    """Turn WebVTT cues into a de-duplicated reading transcript."""
    output_words: list[str] = []
    blocks = re.split(r"\n\s*\n", vtt.replace("\r\n", "\n"))
    for block in blocks:
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        timestamp_index = next(
            (index for index, line in enumerate(lines) if TIMESTAMP_RE.match(line)),
            None,
        )
        if timestamp_index is None:
            continue
        payload = " ".join(lines[timestamp_index + 1 :])
        cue = clean_caption_text(payload)
        _append_with_overlap(output_words, cue.split())
    return " ".join(output_words).strip()


def trim_closing_sponsor(
    text: str,
    sponsor_terms: tuple[str, ...] = (),
    safety_cap: float | None = None,
) -> tuple[str, dict[str, object]]:
    """Trim a detected sponsor close from a derived copy, never the raw VTT."""
    candidates: list[tuple[int, str]] = []
    floor = int(len(text) * 0.45)
    for term in sponsor_terms:
        match = re.search(rf"\b{re.escape(term)}\b", text[floor:], re.IGNORECASE)
        if match:
            candidates.append((floor + match.start(), f"description sponsor term: {term}"))
    match = SPONSOR_RE.search(text, floor)
    if match:
        candidates.append((match.start(), "explicit sponsor marker"))
    if candidates:
        marker_at, marker_reason = min(candidates)
        if safety_cap is not None and marker_at / max(1, len(text)) > safety_cap:
            marker_at = int(len(text) * safety_cap)
            marker_reason = f"{marker_reason}; news-format end-section safety cap"
        previous_stops = [text.rfind(stop, floor, marker_at) for stop in ".!?"]
        previous_stop = max(previous_stops)
        trim_at = previous_stop + 1 if previous_stop >= floor else marker_at
        fraction = trim_at / max(1, len(text))
        trimmed = text[:trim_at].rstrip()
        return trimmed, {
            "trimmed": True,
            "reason": marker_reason,
            "marker_fraction": round(fraction, 3),
            "sponsor_terms": list(sponsor_terms),
        }
    if safety_cap is not None:
        marker_at = int(len(text) * safety_cap)
        previous_stops = [text.rfind(stop, floor, marker_at) for stop in ".!?"]
        previous_stop = max(previous_stops)
        trim_at = previous_stop + 1 if previous_stop >= floor else marker_at
        return text[:trim_at].rstrip(), {
            "trimmed": True,
            "reason": "news-format end-section safety cap",
            "marker_fraction": round(trim_at / max(1, len(text)), 3),
            "sponsor_terms": list(sponsor_terms),
        }
    match = SPONSOR_RE.search(text)
    if not match:
        return text, {
            "trimmed": False,
            "reason": "no closing sponsor marker",
            "sponsor_terms": list(sponsor_terms),
        }
    fraction = match.start() / max(1, len(text))
    if fraction < 0.58:
        return text, {
            "trimmed": False,
            "reason": "marker appears before closing section",
            "marker_fraction": round(fraction, 3),
        }
    trimmed = text[: match.start()].rstrip()
    return trimmed, {
        "trimmed": True,
        "reason": "closing sponsor marker",
        "marker_fraction": round(fraction, 3),
    }


def sponsor_terms_from_info(folder: Path, video_id: str) -> tuple[str, ...]:
    info_path = folder / f"{video_id}.info.json"
    if not info_path.is_file():
        info_path = folder / f"{video_id}.metadata.json"
    if not info_path.is_file():
        return ()
    info = json.loads(info_path.read_text(encoding="utf-8"))
    description = str(info.get("description") or "")
    first_paragraph = description.split("\n\n", 1)[0]
    terms = []
    for host in URL_HOST_RE.findall(first_paragraph):
        labels = host.casefold().split(".")
        if len(labels) < 2:
            continue
        term = re.sub(r"[^a-z0-9-]", "", labels[-2])
        if len(term) >= 4 and term not in {"fireship", "youtube", "youtu", "bytes"}:
            terms.append(term)
    return tuple(dict.fromkeys(terms))


def compact_raw_sources(output: Path, selected: list[dict[str, object]]) -> None:
    """Keep one raw timing source and compact the oversized yt-dlp metadata."""
    metadata_fields = (
        "id",
        "title",
        "description",
        "channel",
        "channel_id",
        "uploader",
        "upload_date",
        "timestamp",
        "duration",
        "view_count",
        "like_count",
        "webpage_url",
        "original_url",
        "thumbnail",
    )
    for row in selected:
        video_id = str(row["id"])
        folder = output / "raw" / video_id
        info_path = folder / f"{video_id}.info.json"
        compact_path = folder / f"{video_id}.metadata.json"
        if info_path.is_file():
            info = json.loads(info_path.read_text(encoding="utf-8"))
            compact = {key: info.get(key) for key in metadata_fields}
            compact_path.write_text(
                json.dumps(compact, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            info_path.unlink()
        vtts = sorted(folder.glob(f"{video_id}*.vtt"))
        if len(vtts) > 1:
            keeper = choose_vtt(folder, video_id)
            if keeper is None:
                continue
            keeper_bytes = keeper.read_bytes()
            for candidate in vtts:
                if candidate != keeper and candidate.read_bytes() == keeper_bytes:
                    candidate.unlink()


def flat_catalog(channel: str, yt_dlp: str) -> list[dict[str, object]]:
    command = [
        yt_dlp,
        "--flat-playlist",
        "--dump-json",
        "--ignore-errors",
        f"{channel.rstrip('/')}/videos",
    ]
    result = run(command)
    rows = []
    for rank, line in enumerate(result.stdout.splitlines(), start=1):
        if not line.strip().startswith("{"):
            continue
        item = json.loads(line)
        video_id = item.get("id")
        if not video_id:
            continue
        rows.append(
            {
                "rank_recency": rank,
                "id": video_id,
                "title": item.get("title") or "",
                "views": int(item.get("view_count") or 0),
                "duration": int(item.get("duration") or 0),
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "tab": "videos",
            }
        )
    if not rows:
        raise SystemExit("yt-dlp returned no Fireship catalog rows")
    return rows


def select_study_set(
    catalog: list[dict[str, object]],
    *,
    latest: int,
    top: int,
    reports: int,
    explainers: int,
) -> list[dict[str, object]]:
    """Select recent, all-time popular, news-format, and 100 Seconds examples."""
    reasons: dict[str, set[str]] = defaultdict(set)

    def add(rows: list[dict[str, object]], label: str, limit: int) -> None:
        for row in rows[:limit]:
            reasons[str(row["id"])].add(label)

    add(catalog, "latest", latest)
    popular = sorted(catalog, key=lambda row: int(row["views"]), reverse=True)
    add(popular, "top_views", top)
    report_candidates = [
        row
        for row in catalog
        if 180 <= int(row["duration"]) <= 540
        and " in 100 seconds" not in str(row["title"]).casefold()
    ]
    add(
        sorted(report_candidates, key=lambda row: int(row["views"]), reverse=True),
        "news_explainer",
        reports,
    )
    short_explainers = [
        row
        for row in catalog
        if " in 100 seconds" in str(row["title"]).casefold()
    ]
    add(
        sorted(short_explainers, key=lambda row: int(row["views"]), reverse=True),
        "100_seconds",
        explainers,
    )

    selected = []
    for row in catalog:
        video_id = str(row["id"])
        if video_id in reasons:
            selected.append({**row, "selection_reasons": sorted(reasons[video_id])})
    return selected


def write_catalogs(
    output: Path,
    catalog: list[dict[str, object]],
    selected: list[dict[str, object]],
) -> None:
    output.mkdir(parents=True, exist_ok=True)
    (output / "catalog.json").write_text(
        json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (output / "selection.json").write_text(
        json.dumps(selected, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    columns = ["rank_recency", "id", "title", "views", "duration", "url", "tab"]
    with (output / "catalog.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows({key: row.get(key, "") for key in columns} for row in catalog)
    with (output / "selection.csv").open("w", newline="", encoding="utf-8") as handle:
        fields = columns + ["selection_reasons"]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in selected:
            writer.writerow(
                {
                    **{key: row.get(key, "") for key in columns},
                    "selection_reasons": ",".join(row["selection_reasons"]),
                }
            )


def download_sources(output: Path, selected: list[dict[str, object]], yt_dlp: str) -> None:
    raw = output / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    archive = output / "download-archive.txt"
    urls = [str(row["url"]) for row in selected]
    command = [
        yt_dlp,
        "--ignore-errors",
        "--skip-download",
        "--write-subs",
        "--write-auto-subs",
        "--sub-langs",
        "en.*,en",
        "--sub-format",
        "vtt",
        "--write-thumbnail",
        "--convert-thumbnails",
        "jpg",
        "--write-info-json",
        "--download-archive",
        str(archive),
        "-o",
        str(raw / "%(id)s" / "%(id)s.%(ext)s"),
        *urls,
    ]
    run(command)


def choose_vtt(folder: Path, video_id: str) -> Path | None:
    candidates = list(folder.glob(f"{video_id}*.vtt"))
    if not candidates:
        return None
    return sorted(
        candidates,
        key=lambda path: (
            0 if path.name.endswith(".en.vtt") else 1,
            0 if ".en-orig." in path.name else 1,
            len(path.name),
        ),
    )[0]


def build_reading_copies(
    output: Path, selected: list[dict[str, object]]
) -> tuple[list[dict[str, object]], list[str]]:
    transcripts = output / "transcripts"
    editorial = output / "editorial-transcripts"
    thumbnails = output / "thumbnails"
    transcripts.mkdir(exist_ok=True)
    editorial.mkdir(exist_ok=True)
    thumbnails.mkdir(exist_ok=True)
    results = []
    failures = []
    for row in selected:
        video_id = str(row["id"])
        folder = output / "raw" / video_id
        vtt_path = choose_vtt(folder, video_id)
        if vtt_path is None:
            failures.append(video_id)
            continue
        clean = vtt_to_text(vtt_path.read_text(encoding="utf-8"))
        if not clean:
            failures.append(video_id)
            continue
        sponsor_terms = sponsor_terms_from_info(folder, video_id)
        reasons = set(row["selection_reasons"])
        safety_cap = (
            0.80
            if reasons.intersection({"latest", "news_explainer"})
            and " in 100 seconds" not in str(row["title"]).casefold()
            else None
        )
        editorial_text, sponsor = trim_closing_sponsor(
            clean, sponsor_terms, safety_cap=safety_cap
        )
        (transcripts / f"{video_id}.txt").write_text(clean + "\n", encoding="utf-8")
        (editorial / f"{video_id}.txt").write_text(
            editorial_text + "\n", encoding="utf-8"
        )
        for thumbnail in sorted(folder.glob(f"{video_id}*.jpg")):
            shutil.copy2(thumbnail, thumbnails / f"{video_id}.jpg")
            break
        results.append(
            {
                **row,
                "raw_vtt": str(vtt_path.relative_to(output.parent.parent)),
                "transcript": str(
                    (transcripts / f"{video_id}.txt").relative_to(output.parent.parent)
                ),
                "editorial_transcript": str(
                    (editorial / f"{video_id}.txt").relative_to(output.parent.parent)
                ),
                "transcript_words": len(WORD_RE.findall(clean)),
                "editorial_words": len(WORD_RE.findall(editorial_text)),
                "sponsor_handling": sponsor,
            }
        )
    return results, failures


def build_contact_sheet(
    output: Path,
    rows: list[dict[str, object]],
    name: str,
    ffmpeg: str,
) -> dict[str, object]:
    """Render a 30-thumbnail review sheet and preserve its ordered index."""
    rows = rows[:30]
    available = [
        row for row in rows if (output / "thumbnails" / f"{row['id']}.jpg").is_file()
    ]
    if not available:
        raise SystemExit(f"no thumbnails available for {name} contact sheet")
    sheets = output / "contact-sheets"
    sheets.mkdir(exist_ok=True)
    destination = sheets / f"{name}.jpg"
    with tempfile.TemporaryDirectory(prefix=f"fireship-{name}-") as temp_name:
        temp = Path(temp_name)
        for index, row in enumerate(available, start=1):
            source = output / "thumbnails" / f"{row['id']}.jpg"
            (temp / f"{index:03d}.jpg").symlink_to(source)
        run(
            [
                ffmpeg,
                "-hide_banner",
                "-loglevel",
                "error",
                "-framerate",
                "1",
                "-start_number",
                "1",
                "-i",
                str(temp / "%03d.jpg"),
                "-vf",
                "scale=384:216:force_original_aspect_ratio=decrease,"
                "pad=384:216:(ow-iw)/2:(oh-ih)/2:color=0x0B0F0D,"
                "tile=5x6:padding=8:margin=8:color=0x0B0F0D",
                "-frames:v",
                "1",
                "-update",
                "1",
                "-y",
                str(destination),
            ]
        )
    return {
        "name": name,
        "path": str(destination.relative_to(output.parent.parent)),
        "rows": available,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--channel", default=DEFAULT_CHANNEL)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--latest", type=int, default=30)
    parser.add_argument("--top", type=int, default=30)
    parser.add_argument("--reports", type=int, default=24)
    parser.add_argument("--explainers", type=int, default=12)
    parser.add_argument("--catalog-only", action="store_true")
    parser.add_argument(
        "--reuse-downloads",
        action="store_true",
        help="Rebuild transcripts, manifests, and contact sheets from existing raw files",
    )
    parser.add_argument(
        "--max-age-days",
        type=int,
        help="Skip a full refresh when the current manifest is newer than this many days",
    )
    args = parser.parse_args()

    output = args.output.resolve()
    manifest_path = output / "manifest.json"
    if args.max_age_days is not None and manifest_path.is_file():
        current = json.loads(manifest_path.read_text(encoding="utf-8"))
        generated_at = datetime.fromisoformat(str(current["generated_at"]))
        if datetime.now().astimezone() - generated_at < timedelta(
            days=args.max_age_days
        ):
            print(
                f"Fireship corpus is fresh ({generated_at.isoformat()}); "
                "skipping refresh"
            )
            return 0
    yt_dlp = shutil.which("yt-dlp")
    if not yt_dlp:
        raise SystemExit("yt-dlp is required and was not found")
    catalog = flat_catalog(args.channel, yt_dlp)
    selected = select_study_set(
        catalog,
        latest=args.latest,
        top=args.top,
        reports=args.reports,
        explainers=args.explainers,
    )
    write_catalogs(output, catalog, selected)
    if args.catalog_only:
        print(f"Cataloged {len(catalog)} videos; selected {len(selected)}")
        return 0

    if not args.reuse_downloads:
        download_sources(output, selected, yt_dlp)
    results, failures = build_reading_copies(output, selected)
    compact_raw_sources(output, selected)
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise SystemExit("ffmpeg is required for thumbnail contact sheets")
    recent_rows = sorted(results, key=lambda row: int(row["rank_recency"]))
    popular_rows = sorted(results, key=lambda row: int(row["views"]), reverse=True)
    contact_sheets = [
        build_contact_sheet(output, recent_rows, "recent-30", ffmpeg),
        build_contact_sheet(output, popular_rows, "popular-30", ffmpeg),
    ]
    (output / "contact-sheets" / "index.json").write_text(
        json.dumps(contact_sheets, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    manifest = {
        "schema_version": 1,
        "channel": args.channel,
        "generated_at": datetime.now().astimezone().isoformat(),
        "catalog_count": len(catalog),
        "selected_count": len(selected),
        "transcript_count": len(results),
        "thumbnail_count": len(list((output / "thumbnails").glob("*.jpg"))),
        "transcript_coverage": round(len(results) / max(1, len(selected)), 4),
        "unavailable_transcripts": failures,
        "contact_sheets": [sheet["path"] for sheet in contact_sheets],
        "selection": results,
    }
    (output / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(
        f"Cataloged {len(catalog)} videos; selected {len(selected)}; "
        f"saved {len(results)} transcripts and {manifest['thumbnail_count']} thumbnails; "
        f"caption-unavailable videos: {len(failures)}"
    )
    return 0 if len(results) / max(1, len(selected)) >= 0.95 else 1


if __name__ == "__main__":
    sys.exit(main())
