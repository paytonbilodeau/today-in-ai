#!/usr/bin/env python3
"""Prepare and submit personal-brand social posts through Postiz.

The command is intentionally conservative. Validation and payload rendering are
local-only. Any external upload requires --confirm-upload, and publishing now or
scheduling a live post also requires --confirm-publish PUBLISH.
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCRIPT_VERSION = "0.3.0"
POSTIZ_VERSION = "2.0.15"
VIDEO_EXTENSIONS = {".mp4", ".mov"}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
PLATFORM_VIDEO_TARGETS = {"instagram", "tiktok", "youtube", "youtube_shorts", "linkedin", "x"}
TIKTOK_PRIVACY_LEVELS = {
    "PUBLIC_TO_EVERYONE",
    "MUTUAL_FOLLOW_FRIENDS",
    "FOLLOWER_OF_CREATOR",
    "SELF_ONLY",
}
COMMERCIAL_CONTENT_OPTIONS = {"none", "own_brand", "third_party", "both"}
X_REPLY_OPTIONS = {"everyone", "following", "mentionedUsers", "subscribers", "verified"}
TIMESTAMP_PATTERN = re.compile(
    r"^(?:(?P<hours>\d+):)?(?P<minutes>\d{1,2}):(?P<seconds>\d{2}(?:\.\d{1,3})?)$"
)
WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = Path(
    os.environ.get(
        "SOCIAL_PUBLISHER_CONFIG_DIR",
        str(Path.home() / ".config" / "social-publisher"),
    )
).expanduser()
ACCOUNT_MAP_PATH = CONFIG_DIR / "accounts.json"
DATA_DIR = Path(
    os.environ.get(
        "SOCIAL_PUBLISHER_DATA_DIR",
        str(Path.home() / ".local" / "share" / "social-publisher"),
    )
).expanduser()
RECEIPTS_DIR = DATA_DIR / "receipts"


class PublisherError(RuntimeError):
    """A user-actionable publishing error."""


@dataclass(frozen=True)
class VideoInfo:
    path: str
    size_bytes: int
    duration_seconds: float
    width: int
    height: int
    fps: float
    video_codec: str
    audio_codec: str
    bitrate: int

    @property
    def orientation(self) -> str:
        if self.height > self.width:
            return "vertical"
        if self.width > self.height:
            return "horizontal"
        return "square"

    def as_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "size_bytes": self.size_bytes,
            "duration_seconds": round(self.duration_seconds, 3),
            "width": self.width,
            "height": self.height,
            "fps": round(self.fps, 3),
            "orientation": self.orientation,
            "video_codec": self.video_codec,
            "audio_codec": self.audio_codec,
            "bitrate": self.bitrate,
        }


def emit(payload: Any) -> None:
    print(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=False))


def run_command(command: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            command,
            check=check,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as exc:
        raise PublisherError(f"Required command not found: {command[0]}") from exc
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or exc.stdout or str(exc)).strip()
        raise PublisherError(detail) from exc


def parse_rate(rate: str | None) -> float:
    if not rate or rate in {"0/0", "N/A"}:
        return 0.0
    if "/" in rate:
        numerator, denominator = rate.split("/", 1)
        try:
            return float(numerator) / float(denominator)
        except (ValueError, ZeroDivisionError):
            return 0.0
    try:
        return float(rate)
    except ValueError:
        return 0.0


def inspect_video(path: Path) -> VideoInfo:
    path = path.expanduser().resolve()
    if not path.is_file():
        raise PublisherError(f"Video not found: {path}")
    if path.suffix.lower() not in VIDEO_EXTENSIONS:
        raise PublisherError("Video must be .mp4 or .mov")

    result = run_command(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_streams",
            "-show_format",
            "-of",
            "json",
            str(path),
        ]
    )
    try:
        probe = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise PublisherError("ffprobe returned invalid JSON") from exc

    streams = probe.get("streams", [])
    video_stream = next((stream for stream in streams if stream.get("codec_type") == "video"), None)
    audio_stream = next((stream for stream in streams if stream.get("codec_type") == "audio"), None)
    if not video_stream:
        raise PublisherError("No video stream found")

    format_info = probe.get("format", {})
    duration = float(format_info.get("duration") or video_stream.get("duration") or 0)
    bitrate = int(float(format_info.get("bit_rate") or 0))
    return VideoInfo(
        path=str(path),
        size_bytes=path.stat().st_size,
        duration_seconds=duration,
        width=int(video_stream.get("width") or 0),
        height=int(video_stream.get("height") or 0),
        fps=parse_rate(video_stream.get("avg_frame_rate") or video_stream.get("r_frame_rate")),
        video_codec=str(video_stream.get("codec_name") or "unknown"),
        audio_codec=str((audio_stream or {}).get("codec_name") or "none"),
        bitrate=bitrate,
    )


def compatibility_report(info: VideoInfo) -> dict[str, list[str]]:
    mib = info.size_bytes / (1024 * 1024)
    gib = mib / 1024
    report: dict[str, list[str]] = {
        "master": [],
        "instagram": [],
        "tiktok": [],
        "youtube": [],
        "linkedin": [],
        "x_api": [],
    }

    if Path(info.path).suffix.lower() != ".mp4":
        report["master"].append("Convert MOV to MP4 H.264/AAC for the most reliable cross-post.")
    if info.video_codec not in {"h264", "hevc"}:
        report["master"].append(f"Video codec is {info.video_codec}; H.264 is the safest common codec.")
    if info.audio_codec not in {"aac", "none"}:
        report["master"].append(f"Audio codec is {info.audio_codec}; AAC is the safest common codec.")

    if info.duration_seconds < 3 or info.duration_seconds > 900:
        report["instagram"].append("Instagram API Reels support 3 seconds to 15 minutes.")
    if gib > 1:
        report["instagram"].append("Instagram API Reels have a 1 GB file limit.")
    if info.fps and not 23 <= info.fps <= 60:
        report["instagram"].append("Instagram expects 23 to 60 FPS.")
    if info.orientation == "vertical" and (info.width > 1080 or info.height > 1920):
        report["instagram"].append(
            "For reliable Postiz Reel publishing, set media.platform_videos.instagram "
            "to a 1080x1920 delivery copy before uploading a larger vertical master."
        )

    if info.duration_seconds > 600:
        report["tiktok"].append("TikTok Content Posting API accepts at most 10 minutes; use browser fallback.")
    if gib > 4:
        report["tiktok"].append("TikTok Content Posting API has a 4 GB file limit.")
    if info.fps and not 23 <= info.fps <= 60:
        report["tiktok"].append("TikTok Content Posting API expects 23 to 60 FPS.")

    if info.duration_seconds < 3 or info.duration_seconds > 1800:
        report["linkedin"].append("LinkedIn video posts support 3 seconds to 30 minutes.")
    if gib > 5:
        report["linkedin"].append("LinkedIn Videos API has a 5 GB file limit.")

    if info.duration_seconds > 140:
        report["x_api"].append("X API tweet_video is limited to 140 seconds; use x.com browser upload for long video.")
    if mib > 512:
        report["x_api"].append("X API video upload is limited to 512 MB; use x.com browser upload if eligible.")
    if info.fps > 60:
        report["x_api"].append("X API video upload supports at most 60 FPS.")

    return report


def default_search_roots() -> list[Path]:
    candidates = [
        Path.home() / "Movies" / "OBS Recordings",
        Path.home() / "Movies",
        WORKSPACE_ROOT / ".tmp",
    ]
    return [path for path in candidates if path.exists()]


def find_videos(query: str) -> list[dict[str, Any]]:
    normalized = query.lower().replace(" ", "")
    matches: list[tuple[float, Path]] = []
    seen: set[Path] = set()
    for root in default_search_roots():
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in VIDEO_EXTENSIONS:
                continue
            resolved = path.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            candidate = path.stem.lower().replace(" ", "")
            score = difflib.SequenceMatcher(None, normalized, candidate).ratio()
            if normalized in candidate:
                score += 1
            matches.append((score, resolved))
    matches.sort(key=lambda item: (item[0], item[1].stat().st_mtime), reverse=True)
    return [
        {
            "path": str(path),
            "score": round(score, 3),
            "size_bytes": path.stat().st_size,
            "modified": datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat(),
        }
        for score, path in matches[:10]
    ]


def base_manifest(workflow: str, video: Path) -> dict[str, Any]:
    video_path = str(video.expanduser().resolve())
    disclosures = {
        "ai_generated": False,
        "paid_promotion": False,
        "made_for_kids": False,
    }
    if workflow == "short":
        return {
            "schema_version": 1,
            "workflow": "short",
            "quality": {
                "mode": "highest_supported",
                "preserve_source": True,
                "allow_upscale": False,
            },
            "publish_at": None,
            "media": {
                "video": video_path,
                "platform_videos": {},
                "thumbnail": None,
                "images": [],
            },
            "disclosures": disclosures,
            "targets": {
                "instagram": {
                    "enabled": True,
                    "method": "postiz",
                    "caption": "",
                    "post_type": "reel",
                    "trial_reel": True,
                    "graduation_strategy": "MANUAL",
                    "audio": None,
                },
                "tiktok": {
                    "enabled": True,
                    "method": "postiz",
                    "caption": "",
                    "privacy": "PUBLIC_TO_EVERYONE",
                    "allow_comments": True,
                    "allow_duet": False,
                    "allow_stitch": False,
                    "commercial_content": "none",
                },
                "youtube_shorts": {
                    "enabled": True,
                    "method": "postiz",
                    "account": "youtube_payton",
                    "title": "",
                    "description": "",
                    "tags": [],
                    "visibility": "public",
                },
                "linkedin": {
                    "enabled": True,
                    "method": "postiz",
                    "caption": "",
                },
                "x": {
                    "enabled": True,
                    "method": "postiz",
                    "caption": "",
                    "who_can_reply": "everyone",
                },
            },
        }
    if workflow == "long":
        return {
            "schema_version": 1,
            "workflow": "long",
            "quality": {
                "mode": "highest_supported",
                "preserve_source": True,
                "allow_upscale": False,
            },
            "publish_at": None,
            "media": {
                "video": video_path,
                "platform_videos": {},
                "thumbnail": None,
                "images": [],
            },
            "disclosures": disclosures,
            "targets": {
                "youtube": {
                    "enabled": True,
                    "method": "postiz",
                    "account": "youtube_payton",
                    "title": "",
                    "description": "",
                    "tags": [],
                    "visibility": "unlisted",
                    "playlist_id": None,
                    "chapters": [],
                    "chapter_source": "auphonic_or_transcript",
                    "automatic_chapters": True,
                    "automatic_key_moments": True,
                    "monetization": "review_in_studio",
                    "ad_suitability": "review_in_studio",
                    "end_screen": "review_in_studio",
                    "cards": "review_in_studio",
                },
                "tiktok": {
                    "enabled": True,
                    "method": "auto",
                    "caption": "",
                    "privacy": "PUBLIC_TO_EVERYONE",
                    "allow_comments": True,
                    "allow_duet": False,
                    "allow_stitch": False,
                    "commercial_content": "none",
                },
                "x": {
                    "enabled": True,
                    "method": "auto",
                    "caption": "",
                    "who_can_reply": "everyone",
                },
            },
        }
    raise PublisherError("Workflow must be short or long")


def load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.expanduser().read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise PublisherError(f"File not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise PublisherError(f"Invalid JSON in {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise PublisherError("JSON root must be an object")
    return payload


def write_private_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    path.chmod(stat.S_IRUSR | stat.S_IWUSR)


def parse_timestamp(value: str) -> float:
    match = TIMESTAMP_PATTERN.fullmatch(str(value).strip())
    if not match:
        raise PublisherError(f"Invalid chapter timestamp: {value}")
    hours = int(match.group("hours") or 0)
    minutes = int(match.group("minutes"))
    seconds = float(match.group("seconds"))
    if minutes >= 60 or seconds >= 60:
        raise PublisherError(f"Invalid chapter timestamp: {value}")
    return hours * 3600 + minutes * 60 + seconds


def format_youtube_timestamp(seconds: float) -> str:
    total_seconds = max(0, int(seconds))
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds_part = divmod(remainder, 60)
    if hours:
        return f"{hours:02d}:{minutes:02d}:{seconds_part:02d}"
    return f"{minutes:02d}:{seconds_part:02d}"


def normalize_chapters(raw_chapters: Any) -> list[dict[str, str]]:
    if not isinstance(raw_chapters, list):
        raise PublisherError("Chapters must be a list")
    normalized: list[dict[str, str]] = []
    for index, chapter in enumerate(raw_chapters, start=1):
        if not isinstance(chapter, dict):
            raise PublisherError(f"Chapter {index} must be an object")
        title = str(chapter.get("title") or "").strip()
        if not title:
            raise PublisherError(f"Chapter {index} needs a title")
        raw_time = (
            chapter.get("time")
            or chapter.get("start_output")
            or chapter.get("start")
        )
        raw_seconds = chapter.get("start_output_sec")
        if raw_seconds is None:
            raw_seconds = chapter.get("start_sec")
        if raw_time is not None:
            seconds = parse_timestamp(str(raw_time))
        elif raw_seconds is not None:
            try:
                seconds = float(raw_seconds)
            except (TypeError, ValueError) as exc:
                raise PublisherError(f"Chapter {index} has an invalid start time") from exc
        else:
            raise PublisherError(f"Chapter {index} needs a timestamp")
        normalized.append({"time": format_youtube_timestamp(seconds), "title": title})
    return normalized


def load_chapters(path: Path) -> list[dict[str, str]]:
    path = path.expanduser().resolve()
    try:
        content = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise PublisherError(f"Chapter file not found: {path}") from exc
    if path.suffix.lower() == ".json":
        try:
            payload = json.loads(content)
        except json.JSONDecodeError as exc:
            raise PublisherError(f"Invalid chapter JSON in {path}: {exc}") from exc
        if isinstance(payload, dict):
            payload = payload.get("chapters")
        return normalize_chapters(payload)

    raw_chapters: list[dict[str, str]] = []
    in_chapter_block = "CHAPTERS:" not in content.upper()
    for raw_line in content.splitlines():
        line = raw_line.strip()
        if line.upper() == "CHAPTERS:":
            in_chapter_block = True
            continue
        if not in_chapter_block or not line:
            continue
        match = re.match(r"^(\d+(?::\d{1,2})?:\d{2}(?:\.\d{1,3})?)\s+(.+)$", line)
        if match:
            raw_chapters.append({"time": match.group(1), "title": match.group(2)})
    if not raw_chapters:
        raise PublisherError(f"No timestamped chapters found in {path}")
    return normalize_chapters(raw_chapters)


def youtube_description(target: dict[str, Any]) -> str:
    description = str(target.get("description") or "").rstrip()
    chapters = normalize_chapters(target.get("chapters", []))
    if not chapters:
        return description
    chapter_text = "\n".join(f"{chapter['time']} {chapter['title']}" for chapter in chapters)
    return f"{description}\n\nChapters\n{chapter_text}".strip()


def import_chapters(manifest_path: Path, chapters_path: Path) -> dict[str, Any]:
    manifest_path = manifest_path.expanduser().resolve()
    manifest = load_json(manifest_path)
    youtube = manifest.get("targets", {}).get("youtube")
    if not isinstance(youtube, dict):
        raise PublisherError("The manifest has no long-form YouTube target")
    chapters = load_chapters(chapters_path)
    youtube["chapters"] = chapters
    youtube["chapter_source"] = str(chapters_path.expanduser().resolve())
    youtube["automatic_chapters"] = False
    validation = validate_manifest(manifest)
    if not validation["ok"]:
        raise PublisherError("Imported chapters are invalid: " + "; ".join(validation["errors"]))
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {
        "ok": True,
        "manifest": str(manifest_path),
        "chapter_source": str(chapters_path.expanduser().resolve()),
        "chapters": chapters,
        "warnings": validation["warnings"],
    }


def resolve_methods(manifest: dict[str, Any], info: VideoInfo | None) -> tuple[dict[str, Any], list[str]]:
    resolved = json.loads(json.dumps(manifest))
    followups: list[str] = []
    targets = resolved.get("targets", {})
    x_target = targets.get("x", {})
    if x_target.get("enabled") and x_target.get("method") == "auto":
        if info and (info.duration_seconds > 140 or info.size_bytes > 512 * 1024 * 1024):
            x_target["method"] = "browser"
            followups.append("Upload the long X video through x.com in the logged-in browser; the public API limit is 140 seconds/512 MB.")
        else:
            x_target["method"] = "postiz"
    if (
        x_target.get("enabled")
        and x_target.get("method") != "browser"
        and re.search(r"https?://", str(x_target.get("caption") or ""))
    ):
        x_target["method"] = "browser"
        followups.append("Publish the X post in the logged-in browser because this Postiz X connection strips links.")

    tiktok_target = targets.get("tiktok", {})
    if tiktok_target.get("enabled") and tiktok_target.get("method") == "auto":
        if info and info.duration_seconds > 600:
            tiktok_target["method"] = "browser"
            followups.append("Upload the long TikTok video in the browser; the Content Posting API limit is 10 minutes.")
        else:
            tiktok_target["method"] = "postiz"

    youtube_target = targets.get("youtube", {})
    if youtube_target.get("enabled"):
        chapter_check = (
            "verify the manual chapter preview"
            if youtube_target.get("chapters")
            else "confirm automatic chapters and key moments are allowed"
        )
        followups.append(
            "Finish YouTube Studio checks: monetization, ad suitability, copyright, "
            f"{chapter_check}, end screen, cards, and final visibility."
        )
        if youtube_target.get("playlist_id"):
            followups.append("Add the YouTube video to its selected playlist in YouTube Studio; this Postiz connection does not expose playlist settings.")
    return resolved, followups


def validate_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    if manifest.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    workflow = manifest.get("workflow")
    if workflow not in {"short", "long", "image"}:
        errors.append("workflow must be short, long, or image")
    quality = manifest.get("quality") or {
        "mode": "highest_supported",
        "preserve_source": True,
        "allow_upscale": False,
    }
    if not isinstance(quality, dict) or quality.get("mode") != "highest_supported":
        errors.append("quality.mode must be highest_supported")
    elif quality.get("preserve_source", True) is not True:
        errors.append("quality.preserve_source must be true")
    elif quality.get("allow_upscale", False) is not False:
        errors.append("quality.allow_upscale must be false")
    media = manifest.get("media")
    if not isinstance(media, dict):
        errors.append("media must be an object")
        return {"ok": False, "errors": errors, "warnings": warnings}
    info: VideoInfo | None = None
    platform_video_info: dict[str, VideoInfo] = {}
    images: list[str] = []
    if workflow == "image":
        raw_images = media.get("images")
        if not isinstance(raw_images, list) or not raw_images:
            errors.append("media.images must contain at least one image")
        elif len(raw_images) > 10:
            errors.append("media.images supports at most 10 images")
        else:
            for raw_image in raw_images:
                path = Path(str(raw_image)).expanduser().resolve()
                if not path.is_file():
                    errors.append(f"Image not found: {path}")
                elif path.suffix.lower() not in IMAGE_EXTENSIONS:
                    errors.append(f"Unsupported image type: {path}")
                else:
                    images.append(str(path))
    else:
        if not media.get("video"):
            errors.append("media.video is required")
            return {"ok": False, "errors": errors, "warnings": warnings}
        try:
            info = inspect_video(Path(media["video"]))
        except PublisherError as exc:
            errors.append(str(exc))
            return {"ok": False, "errors": errors, "warnings": warnings}
        raw_platform_videos = media.get("platform_videos", {})
        if not isinstance(raw_platform_videos, dict):
            errors.append("media.platform_videos must be an object")
        else:
            for platform, raw_path in raw_platform_videos.items():
                if platform not in PLATFORM_VIDEO_TARGETS:
                    errors.append(f"Unsupported media.platform_videos target: {platform}")
                    continue
                try:
                    derivative = inspect_video(Path(str(raw_path)))
                except PublisherError as exc:
                    errors.append(f"media.platform_videos.{platform}: {exc}")
                    continue
                platform_video_info[platform] = derivative
                if abs(derivative.duration_seconds - info.duration_seconds) > 0.5:
                    errors.append(
                        f"media.platform_videos.{platform} duration must match the master within 0.5 seconds"
                    )
                if derivative.orientation != info.orientation:
                    errors.append(
                        f"media.platform_videos.{platform} orientation must match the master"
                    )

    targets = manifest.get("targets")
    if not isinstance(targets, dict) or not any(
        isinstance(target, dict) and target.get("enabled") for target in targets.values()
    ):
        errors.append("At least one target must be enabled")
        targets = {}

    publish_at = manifest.get("publish_at")
    if publish_at:
        try:
            parsed_publish_at = datetime.fromisoformat(str(publish_at).replace("Z", "+00:00"))
        except ValueError:
            errors.append("publish_at must be an ISO 8601 date and time")
        else:
            if parsed_publish_at.tzinfo is None:
                errors.append("publish_at must include a timezone offset")

    for name, target in targets.items():
        if not isinstance(target, dict) or not target.get("enabled"):
            continue
        if target.get("method", "postiz") not in {"postiz", "browser", "auto"}:
            errors.append(f"targets.{name}.method must be postiz, browser, or auto")
        if name in {"youtube", "youtube_shorts"}:
            if not str(target.get("title", "")).strip():
                errors.append(f"targets.{name}.title is required")
            if len(str(target.get("title", ""))) > 100:
                errors.append(f"targets.{name}.title must be 100 characters or fewer")
            if not target.get("account"):
                errors.append(f"targets.{name}.account is required")
            if target.get("visibility") not in {"public", "unlisted", "private"}:
                errors.append(f"targets.{name}.visibility must be public, unlisted, or private")
            if name == "youtube":
                try:
                    chapters = normalize_chapters(target.get("chapters", []))
                except PublisherError as exc:
                    errors.append(f"targets.youtube.chapters: {exc}")
                    chapters = []
                if chapters:
                    chapter_seconds = [parse_timestamp(chapter["time"]) for chapter in chapters]
                    if len(chapters) < 3:
                        errors.append("targets.youtube.chapters needs at least three chapters")
                    if chapter_seconds[0] != 0:
                        errors.append("targets.youtube.chapters must start at 00:00")
                    for previous, current in zip(chapter_seconds, chapter_seconds[1:]):
                        if current <= previous:
                            errors.append("targets.youtube.chapters must be in ascending order")
                            break
                        if current - previous < 10:
                            errors.append("Each YouTube chapter must be at least 10 seconds long")
                            break
                    if info and chapter_seconds[-1] >= info.duration_seconds:
                        errors.append("The final YouTube chapter must start before the video ends")
                    elif info and info.duration_seconds - chapter_seconds[-1] < 10:
                        errors.append("The final YouTube chapter must be at least 10 seconds long")
                    if target.get("automatic_chapters"):
                        warnings.append(
                            "youtube: Manual timestamps override YouTube automatic chapters; set automatic_chapters to false."
                        )
                elif not target.get("automatic_chapters", True):
                    warnings.append("youtube: No manual chapters are present and automatic chapters are disabled.")
                try:
                    rendered_description = youtube_description(target)
                except PublisherError:
                    rendered_description = str(target.get("description") or "")
                if len(rendered_description) > 5000:
                    errors.append("targets.youtube description plus chapters must be 5,000 characters or fewer")
        else:
            if not str(target.get("caption", "")).strip():
                errors.append(f"targets.{name}.caption is required")
            caption_limits = {"instagram": 2200, "tiktok": 2000, "linkedin": 3000, "x": 4000}
            if name in caption_limits and len(str(target.get("caption") or "")) > caption_limits[name]:
                errors.append(
                    f"targets.{name}.caption must be {caption_limits[name]:,} characters or fewer"
                )
        if name == "instagram" and target.get("post_type") not in {"reel", "story", "feed"}:
            errors.append("targets.instagram.post_type must be reel, story, or feed")
        if name == "tiktok":
            if target.get("privacy") not in TIKTOK_PRIVACY_LEVELS:
                errors.append("targets.tiktok.privacy is invalid")
            if target.get("commercial_content", "none") not in COMMERCIAL_CONTENT_OPTIONS:
                errors.append("targets.tiktok.commercial_content is invalid")
            if target.get("content_posting_method") not in {None, "DIRECT_POST", "UPLOAD"}:
                errors.append(
                    "targets.tiktok.content_posting_method must be DIRECT_POST or UPLOAD"
                )
        if name == "x" and target.get("who_can_reply", "everyone") not in X_REPLY_OPTIONS:
            errors.append("targets.x.who_can_reply is invalid")

    resolved, followups = resolve_methods(manifest, info)
    if info:
        compatibility = compatibility_report(info)
        for platform, messages in compatibility.items():
            warnings.extend(f"{platform}: {message}" for message in messages)
    if manifest.get("workflow") == "short" and info and info.orientation != "vertical":
        warnings.append("master: Short-form master is not vertical 9:16.")
    if media.get("thumbnail") and not Path(str(media["thumbnail"])).expanduser().is_file():
        errors.append(f"Thumbnail not found: {media['thumbnail']}")

    return {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "video": info.as_dict() if info else None,
        "platform_videos": {
            platform: derivative.as_dict()
            for platform, derivative in platform_video_info.items()
        },
        "images": images,
        "resolved_manifest": resolved,
        "browser_followups": followups,
    }


def load_account_map(path: Path = ACCOUNT_MAP_PATH) -> dict[str, Any]:
    payload = load_json(path)
    if "postiz" not in payload or not isinstance(payload["postiz"], dict):
        raise PublisherError(f"Invalid account map: {path}")
    return payload


def integration_alias(target_name: str, target: dict[str, Any]) -> str:
    return str(target.get("account") or target_name)


def media_object(upload: dict[str, Any], fallback_id: str) -> dict[str, str]:
    path = upload.get("path") or upload.get("url")
    if not path:
        raise PublisherError(f"Upload result missing path for {fallback_id}")
    return {"id": str(upload.get("id") or fallback_id), "path": str(path)}


def postiz_settings(name: str, target: dict[str, Any], manifest: dict[str, Any], uploads: dict[str, Any]) -> dict[str, Any]:
    disclosures = manifest.get("disclosures", {})
    if name == "instagram":
        settings = {
            "__type": "instagram",
            "post_type": "story" if target.get("post_type") == "story" else "post",
            "is_trial_reel": bool(target.get("trial_reel", False)),
            "graduation_strategy": target.get("graduation_strategy", "MANUAL"),
            "collaborators": target.get("collaborators", []),
        }
        if isinstance(target.get("audio"), dict) and target["audio"].get("id"):
            settings["audio"] = target["audio"]
        return settings
    if name == "tiktok":
        commercial = target.get("commercial_content", "none")
        image_count = len(manifest.get("media", {}).get("images", []))
        default_posting_method = (
            "UPLOAD"
            if manifest.get("workflow") == "image" and image_count > 1
            else "DIRECT_POST"
        )
        settings = {
            "__type": "tiktok",
            "title": target.get("title", target.get("caption", "")[:90]),
            "privacy_level": target.get("privacy", "PUBLIC_TO_EVERYONE"),
            "duet": bool(target.get("allow_duet", False)),
            "stitch": bool(target.get("allow_stitch", False)),
            "comment": bool(target.get("allow_comments", True)),
            "autoAddMusic": "no",
            "brand_content_toggle": commercial in {"third_party", "both"},
            "brand_organic_toggle": commercial in {"own_brand", "both"},
            "content_posting_method": target.get(
                "content_posting_method", default_posting_method
            ),
        }
        if manifest.get("workflow") != "image":
            settings["video_made_with_ai"] = bool(disclosures.get("ai_generated", False))
        return settings
    if name in {"youtube", "youtube_shorts"}:
        settings: dict[str, Any] = {
            "__type": "youtube",
            "title": target.get("title", ""),
            "type": target.get("visibility", "unlisted"),
            "selfDeclaredMadeForKids": "yes" if disclosures.get("made_for_kids") else "no",
            "tags": [
                {"value": str(tag), "label": str(tag)}
                for tag in target.get("tags", [])
            ],
        }
        if uploads.get("thumbnail"):
            settings["thumbnail"] = media_object(uploads["thumbnail"], "thumbnail")
        return settings
    if name == "linkedin":
        return {"__type": "linkedin"}
    if name == "x":
        return {
            "__type": "x",
            "who_can_reply_post": target.get("who_can_reply", "everyone"),
            "made_with_ai": bool(disclosures.get("ai_generated", False)),
            "paid_partnership": bool(disclosures.get("paid_promotion", False)),
        }
    raise PublisherError(f"Unsupported Postiz target: {name}")


def render_postiz_payload(
    manifest: dict[str, Any],
    account_map: dict[str, Any],
    uploads: dict[str, Any],
    *,
    mode: str,
) -> tuple[dict[str, Any], list[str]]:
    info = (
        inspect_video(Path(manifest["media"]["video"]))
        if manifest.get("workflow") != "image"
        else None
    )
    resolved, followups = resolve_methods(manifest, info)
    integrations = account_map.get("postiz", {})
    posts: list[dict[str, Any]] = []
    for name, target in resolved.get("targets", {}).items():
        if not target.get("enabled") or target.get("method") != "postiz":
            continue
        if (
            name == "tiktok"
            and account_map.get("backend") == "postiz_self_hosted"
            and target.get("privacy") != "SELF_ONLY"
            and not account_map.get("tiktok_direct_post_audited", False)
        ):
            followups.append(
                "Use TikTok's logged-in browser uploader. A self-hosted, unaudited TikTok client can only Direct Post as SELF_ONLY."
            )
            continue
        alias = integration_alias(name, target)
        integration_id = integrations.get(alias)
        if not integration_id or str(integration_id).startswith("REPLACE_"):
            raise PublisherError(f"Missing Postiz integration ID for account alias: {alias}")
        content = (
            youtube_description(target)
            if name == "youtube"
            else target.get("description")
            if name == "youtube_shorts"
            else target.get("caption")
        )
        if manifest.get("workflow") == "image":
            image_uploads = uploads.get("images", [])
            post_media = [
                media_object(upload, f"image-{index}")
                for index, upload in enumerate(image_uploads, start=1)
            ]
        else:
            platform_upload = uploads.get("platform_videos", {}).get(name)
            post_media = [
                media_object(
                    platform_upload or uploads.get("video", {}),
                    f"{name}-video" if platform_upload else "video",
                )
            ]
        settings = postiz_settings(name, target, resolved, uploads)
        if name == "tiktok" and settings.get("content_posting_method") == "UPLOAD":
            followups.append(
                "Finish the TikTok carousel from the TikTok app inbox within 24 hours: "
                "restore paragraph spacing if TikTok flattened it, choose a sound, and publish."
            )
        if (
            name in {"youtube", "youtube_shorts"}
            and account_map.get("backend") == "postiz_self_hosted"
            and not account_map.get("youtube_api_audited", False)
            and settings.get("type") != "private"
        ):
            settings["type"] = "private"
            followups.append(
                "The self-hosted YouTube API project is marked unaudited, so visibility was forced to private. Finish visibility in YouTube Studio."
            )
        posts.append(
            {
                "integration": {"id": integration_id},
                "value": [{"content": content or "", "image": post_media}],
                "settings": settings,
            }
        )

    if not posts:
        raise PublisherError("No Postiz targets remain after method routing")
    publish_at = (
        datetime.now(timezone.utc).isoformat()
        if mode == "now"
        else resolved.get("publish_at") or datetime.now(timezone.utc).isoformat()
    )
    return (
        {
            "type": mode,
            "creationMethod": "CLI",
            "date": publish_at,
            "shortLink": False,
            "tags": [],
            "posts": posts,
        },
        followups,
    )


def canonical_fingerprint(manifest: dict[str, Any]) -> str:
    digest = hashlib.sha256()
    digest.update(json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode("utf-8"))
    media = manifest.get("media", {})
    for key in ("video", "thumbnail"):
        raw_path = media.get(key)
        if not raw_path:
            continue
        path = Path(str(raw_path)).expanduser().resolve()
        if path.exists():
            stat_result = path.stat()
            digest.update(f"{path}:{stat_result.st_size}:{stat_result.st_mtime_ns}".encode("utf-8"))
    for platform, raw_path in sorted(media.get("platform_videos", {}).items()):
        path = Path(str(raw_path)).expanduser().resolve()
        if path.exists():
            stat_result = path.stat()
            digest.update(
                f"{platform}:{path}:{stat_result.st_size}:{stat_result.st_mtime_ns}".encode("utf-8")
            )
    for raw_path in media.get("images", []):
        path = Path(str(raw_path)).expanduser().resolve()
        if path.exists():
            stat_result = path.stat()
            digest.update(f"{path}:{stat_result.st_size}:{stat_result.st_mtime_ns}".encode("utf-8"))
    return digest.hexdigest()


def postiz_command() -> list[str]:
    installed = shutil.which("postiz")
    if installed:
        return [installed]
    if shutil.which("npx"):
        return ["npx", "--yes", f"postiz@{POSTIZ_VERSION}"]
    raise PublisherError("Postiz CLI unavailable. Install Node.js/npm or run: npm install -g postiz")


def run_postiz(arguments: list[str]) -> subprocess.CompletedProcess[str]:
    return run_command(postiz_command() + arguments)


def extract_json(text: str) -> Any:
    decoder = json.JSONDecoder()
    for index, character in enumerate(text):
        if character not in "[{":
            continue
        try:
            value, end = decoder.raw_decode(text[index:])
        except json.JSONDecodeError:
            continue
        if not text[index + end :].strip():
            return value
    raise PublisherError("Could not parse JSON from Postiz CLI output")


def submit_manifest(manifest_path: Path, mode: str, confirm_upload: bool, confirm_publish: str | None, force: bool) -> dict[str, Any]:
    if not confirm_upload:
        raise PublisherError("External media upload requires --confirm-upload")
    if mode in {"now", "schedule"} and confirm_publish != "PUBLISH":
        action = "Publishing now" if mode == "now" else "Scheduling"
        raise PublisherError(f"{action} requires --confirm-publish PUBLISH")

    manifest = load_json(manifest_path)
    validation = validate_manifest(manifest)
    if not validation["ok"]:
        raise PublisherError("Manifest validation failed: " + "; ".join(validation["errors"]))
    if mode == "schedule" and not manifest.get("publish_at"):
        raise PublisherError("Scheduled publishing requires publish_at in the manifest")

    fingerprint = canonical_fingerprint(manifest)
    receipt_path = RECEIPTS_DIR / f"{fingerprint}.json"
    if receipt_path.exists() and not force:
        raise PublisherError(f"This manifest was already submitted. Receipt: {receipt_path}")

    account_map = load_account_map()
    render_postiz_payload(
        manifest,
        account_map,
        {
            "video": {"id": "preflight-video", "path": "https://preflight.invalid/video.mp4"},
            "platform_videos": {
                platform: {
                    "id": f"preflight-{platform}-video",
                    "path": f"https://preflight.invalid/{platform}-video.mp4",
                }
                for platform in manifest.get("media", {}).get("platform_videos", {})
            },
            "thumbnail": {"id": "preflight-thumbnail", "path": "https://preflight.invalid/thumbnail.jpg"},
            "images": [
                {"id": f"preflight-image-{index}", "path": f"https://preflight.invalid/image-{index}.png"}
                for index, _ in enumerate(manifest.get("media", {}).get("images", []), start=1)
            ],
        },
        mode=mode,
    )

    auth = run_postiz(["auth:status"])
    if "Credentials are valid" not in auth.stdout:
        raise PublisherError("Postiz is not authenticated. Run: npx postiz@2.0.15 auth:login")

    uploads: dict[str, Any] = {}
    for key in ("video", "thumbnail"):
        raw_path = manifest.get("media", {}).get(key)
        if not raw_path:
            continue
        result = run_postiz(["upload", str(Path(raw_path).expanduser().resolve())])
        uploads[key] = extract_json(result.stdout)
    uploads["platform_videos"] = {}
    for platform, raw_path in manifest.get("media", {}).get("platform_videos", {}).items():
        result = run_postiz(["upload", str(Path(raw_path).expanduser().resolve())])
        uploads["platform_videos"][platform] = extract_json(result.stdout)
    uploads["images"] = []
    for raw_path in manifest.get("media", {}).get("images", []):
        result = run_postiz(["upload", str(Path(raw_path).expanduser().resolve())])
        uploads["images"].append(extract_json(result.stdout))

    payload, followups = render_postiz_payload(manifest, account_map, uploads, mode=mode)
    with tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8", delete=False) as handle:
        json.dump(payload, handle, ensure_ascii=False)
        payload_path = Path(handle.name)
    try:
        created = run_postiz(["posts:create", "--json", str(payload_path)])
        created_payload = extract_json(created.stdout)
    finally:
        payload_path.unlink(missing_ok=True)

    receipt = {
        "schema_version": 1,
        "fingerprint": fingerprint,
        "submitted_at": datetime.now(timezone.utc).isoformat(),
        "mode": mode,
        "manifest": str(manifest_path.expanduser().resolve()),
        "postiz_result": created_payload,
        "browser_followups": followups,
    }
    write_private_json(receipt_path, receipt)
    return {"ok": True, "receipt": str(receipt_path), **receipt}


def doctor(online: bool) -> dict[str, Any]:
    checks: dict[str, Any] = {
        "ffprobe": shutil.which("ffprobe"),
        "ffmpeg": shutil.which("ffmpeg"),
        "node": shutil.which("node"),
        "npx": shutil.which("npx"),
        "postiz_global": shutil.which("postiz"),
        "account_map": str(ACCOUNT_MAP_PATH) if ACCOUNT_MAP_PATH.exists() else None,
        "postiz_credentials": str(Path.home() / ".postiz" / "credentials.json")
        if (Path.home() / ".postiz" / "credentials.json").exists()
        else None,
    }
    checks["local_ready"] = bool(checks["ffprobe"] and (checks["postiz_global"] or checks["npx"]))
    checks["account_ids_ready"] = False
    checks["missing_account_aliases"] = []
    if checks["account_map"]:
        try:
            account_map = load_account_map()
            integrations = account_map.get("postiz", {})
            required_aliases = {"instagram", "tiktok", "linkedin", "x", "youtube_payton"}
            all_aliases = required_aliases | {"youtube_echo"}
            missing_aliases = sorted(
                alias
                for alias in all_aliases
                if not integrations.get(alias)
                or str(integrations.get(alias)).startswith("REPLACE_")
            )
            checks["missing_account_aliases"] = missing_aliases
            checks["account_ids_ready"] = not required_aliases.intersection(missing_aliases)
        except PublisherError as exc:
            checks["account_map_error"] = str(exc)
    checks["configured"] = bool(checks["account_ids_ready"] and checks["postiz_credentials"])
    if online:
        try:
            version = run_postiz(["--version"])
            checks["postiz_version"] = version.stdout.strip()
            status = run_postiz(["auth:status"])
            checks["postiz_authenticated"] = "Credentials are valid" in status.stdout
        except PublisherError as exc:
            checks["online_error"] = str(exc)
    return checks


def init_account_map(backend: str, force: bool) -> dict[str, Any]:
    if ACCOUNT_MAP_PATH.exists() and not force:
        raise PublisherError(f"Account map already exists: {ACCOUNT_MAP_PATH}. Use --force to replace it.")
    payload = {
        "schema_version": 1,
        "backend": backend,
        "tiktok_direct_post_audited": False,
        "youtube_api_audited": False,
        "postiz": {
            "instagram": "REPLACE_WITH_POSTIZ_INTEGRATION_ID",
            "tiktok": "REPLACE_WITH_POSTIZ_INTEGRATION_ID",
            "linkedin": "REPLACE_WITH_POSTIZ_INTEGRATION_ID",
            "x": "REPLACE_WITH_POSTIZ_INTEGRATION_ID",
            "youtube_payton": "REPLACE_WITH_POSTIZ_INTEGRATION_ID",
            "youtube_echo": "REPLACE_WITH_POSTIZ_INTEGRATION_ID",
        },
    }
    write_private_json(ACCOUNT_MAP_PATH, payload)
    return {"ok": True, "path": str(ACCOUNT_MAP_PATH), "backend": backend}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", action="version", version=SCRIPT_VERSION)
    subparsers = parser.add_subparsers(dest="command", required=True)

    doctor_parser = subparsers.add_parser("doctor", help="Check local tools and optional Postiz auth")
    doctor_parser.add_argument("--online", action="store_true")

    find_parser = subparsers.add_parser("find", help="Fuzzy-find a video in standard locations")
    find_parser.add_argument("query")

    inspect_parser = subparsers.add_parser("inspect", help="Inspect video metadata and platform limits")
    inspect_parser.add_argument("video", type=Path)

    template_parser = subparsers.add_parser("template", help="Create a short- or long-form manifest")
    template_parser.add_argument("--workflow", choices=["short", "long"], required=True)
    template_parser.add_argument("--video", type=Path, required=True)
    template_parser.add_argument("--output", type=Path, required=True)
    template_parser.add_argument("--force", action="store_true")

    validate_parser = subparsers.add_parser("validate", help="Validate a manifest without uploading")
    validate_parser.add_argument("manifest", type=Path)

    render_parser = subparsers.add_parser("render", help="Render a Postiz payload without uploading")
    render_parser.add_argument("manifest", type=Path)
    render_parser.add_argument("--accounts", type=Path, default=ACCOUNT_MAP_PATH)
    render_parser.add_argument("--mode", choices=["draft", "now", "schedule"], default="draft")
    render_parser.add_argument("--output", type=Path)

    chapters_parser = subparsers.add_parser(
        "import-chapters",
        help="Import Auphonic or timestamped chapters into a long-form manifest",
    )
    chapters_parser.add_argument("manifest", type=Path)
    chapters_parser.add_argument("chapters", type=Path)

    init_parser = subparsers.add_parser("init-accounts", help="Create the private account alias map")
    init_parser.add_argument("--backend", choices=["postiz_hosted", "postiz_self_hosted"], default="postiz_hosted")
    init_parser.add_argument("--force", action="store_true")

    submit_parser = subparsers.add_parser(
        "submit",
        help="Upload media and create a Postiz draft, publish now, or schedule",
    )
    submit_parser.add_argument("manifest", type=Path)
    submit_parser.add_argument("--mode", choices=["draft", "now", "schedule"], default="draft")
    submit_parser.add_argument("--confirm-upload", action="store_true")
    submit_parser.add_argument("--confirm-publish")
    submit_parser.add_argument("--force", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        if args.command == "doctor":
            emit(doctor(args.online))
        elif args.command == "find":
            emit({"query": args.query, "matches": find_videos(args.query)})
        elif args.command == "inspect":
            info = inspect_video(args.video)
            emit({"video": info.as_dict(), "compatibility": compatibility_report(info)})
        elif args.command == "template":
            if args.output.exists() and not args.force:
                raise PublisherError(f"Output exists: {args.output}. Use --force to replace it.")
            manifest = base_manifest(args.workflow, args.video)
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            emit({"ok": True, "output": str(args.output.resolve()), "workflow": args.workflow})
        elif args.command == "validate":
            validation = validate_manifest(load_json(args.manifest))
            emit(validation)
            return 0 if validation["ok"] else 2
        elif args.command == "render":
            manifest = load_json(args.manifest)
            validation = validate_manifest(manifest)
            if not validation["ok"]:
                raise PublisherError("Manifest validation failed: " + "; ".join(validation["errors"]))
            placeholder_uploads = {
                "video": {"id": "video", "path": "media://video"},
                "platform_videos": {
                    platform: {
                        "id": f"{platform}-video",
                        "path": f"media://{platform}-video",
                    }
                    for platform in manifest.get("media", {}).get("platform_videos", {})
                },
                "images": [
                    {"id": f"image-{index}", "path": f"media://image-{index}"}
                    for index, _ in enumerate(manifest.get("media", {}).get("images", []), start=1)
                ],
            }
            if manifest.get("media", {}).get("thumbnail"):
                placeholder_uploads["thumbnail"] = {"id": "thumbnail", "path": "media://thumbnail"}
            payload, followups = render_postiz_payload(
                manifest,
                load_account_map(args.accounts),
                placeholder_uploads,
                mode=args.mode,
            )
            rendered = {"payload": payload, "browser_followups": followups}
            if args.output:
                args.output.parent.mkdir(parents=True, exist_ok=True)
                args.output.write_text(json.dumps(rendered, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
                emit({"ok": True, "output": str(args.output.resolve()), **rendered})
            else:
                emit(rendered)
        elif args.command == "import-chapters":
            emit(import_chapters(args.manifest, args.chapters))
        elif args.command == "init-accounts":
            emit(init_account_map(args.backend, args.force))
        elif args.command == "submit":
            emit(submit_manifest(args.manifest, args.mode, args.confirm_upload, args.confirm_publish, args.force))
        else:
            raise PublisherError(f"Unknown command: {args.command}")
        return 0
    except PublisherError as exc:
        emit({"ok": False, "error": str(exc)})
        return 2


if __name__ == "__main__":
    sys.exit(main())
