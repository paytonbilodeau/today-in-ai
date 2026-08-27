#!/usr/bin/env python3
"""Apply the locked transparent Today in AI series badge."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path


WORKSPACE = Path("/Users/paytonbilodeau/Documents/Business Vibe Coding")
DEFAULT_MARK = (
    WORKSPACE
    / "today-in-ai/brand/selected/today-in-ai-logo-white-transparent.png"
)
CANVAS_WIDTH = 1920
CANVAS_HEIGHT = 1080
BADGE_WIDTH = 230
BADGE_LEFT = 84
BADGE_BOTTOM = 84


class BadgeError(ValueError):
    """Raised when the locked Today in AI badge cannot be applied safely."""


def probe_image(path: Path) -> dict:
    if not path.is_file():
        raise BadgeError(f"missing image: {path}")
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        raise BadgeError("ffprobe is required")
    command = [
        ffprobe,
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=width,height,pix_fmt",
        "-of",
        "json",
        str(path),
    ]
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    streams = json.loads(result.stdout).get("streams", [])
    if not streams:
        raise BadgeError(f"no image stream found: {path}")
    return streams[0]


def badge_geometry(mark_width: int, mark_height: int) -> dict:
    if mark_width <= 0 or mark_height <= 0:
        raise BadgeError("badge dimensions must be positive")
    rendered_height = round(mark_height * BADGE_WIDTH / mark_width)
    return {
        "canvas_width": CANVAS_WIDTH,
        "canvas_height": CANVAS_HEIGHT,
        "width": BADGE_WIDTH,
        "height": rendered_height,
        "left": BADGE_LEFT,
        "top": CANVAS_HEIGHT - BADGE_BOTTOM - rendered_height,
        "bottom": BADGE_BOTTOM,
    }


def apply_badge(input_path: Path, output_path: Path, mark_path: Path) -> dict:
    input_path = input_path.resolve()
    output_path = output_path.resolve()
    mark_path = mark_path.resolve()

    if input_path == output_path:
        raise BadgeError("input and output paths must differ")
    if output_path.suffix.lower() != ".png":
        raise BadgeError("output must be a PNG")

    source = probe_image(input_path)
    if (source.get("width"), source.get("height")) != (
        CANVAS_WIDTH,
        CANVAS_HEIGHT,
    ):
        raise BadgeError(
            f"input must be {CANVAS_WIDTH}x{CANVAS_HEIGHT}, "
            f"got {source.get('width')}x{source.get('height')}"
        )

    mark = probe_image(mark_path)
    if "a" not in str(mark.get("pix_fmt", "")):
        raise BadgeError("publication mark must contain an alpha channel")

    geometry = badge_geometry(int(mark["width"]), int(mark["height"]))
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise BadgeError("ffmpeg is required")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    filter_graph = (
        f"[1:v]scale={BADGE_WIDTH}:-1:flags=lanczos[badge];"
        f"[0:v][badge]overlay={BADGE_LEFT}:H-h-{BADGE_BOTTOM}:format=auto"
    )
    command = [
        ffmpeg,
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-i",
        str(input_path),
        "-i",
        str(mark_path),
        "-filter_complex",
        filter_graph,
        "-frames:v",
        "1",
        "-c:v",
        "png",
        str(output_path),
    ]
    subprocess.run(command, check=True)

    result = probe_image(output_path)
    if (result.get("width"), result.get("height")) != (
        CANVAS_WIDTH,
        CANVAS_HEIGHT,
    ):
        raise BadgeError("badged output dimensions changed unexpectedly")

    return {
        "status": "pass",
        "input": str(input_path),
        "output": str(output_path),
        "mark": str(mark_path),
        "geometry": geometry,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--mark", type=Path, default=DEFAULT_MARK)
    args = parser.parse_args()

    try:
        result = apply_badge(args.input, args.output, args.mark)
    except (BadgeError, subprocess.CalledProcessError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "fail", "error": str(exc)}, indent=2))
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
