#!/usr/bin/env python3
"""Validate the sourced-image and logo manifest for a Today in AI edition."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlparse


WORKSPACE = Path("~/workspace").expanduser()
TODAY_MARK = "today-in-ai/brand/selected/today-in-ai-logo-white-transparent.png"
AI_MENTORSHIP_PALETTE = {
    "jet_black": "#0B0F0D",
    "old_money_green": "#0F583D",
    "mint_green": "#72DFA5",
    "warm_paper": "#F7F8F4",
    "white": "#FFFFFF",
}
REFERENCE_ROUTES = {"reference_generation", "cutout_composite", "generated_original"}
BADGE_GEOMETRY = {
    "canvas_width_px": 1920,
    "canvas_height_px": 1080,
    "left_px": 84,
    "bottom_px": 84,
    "width_px": 230,
}
ALLOWED_SOURCE_KINDS = {
    "established_meme",
    "official_press_asset",
    "licensed_asset",
    "public_domain_asset",
    "owned_asset",
    "generated_original",
}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
WORD_RE = re.compile(r"[A-Za-z0-9]+(?:['’][A-Za-z0-9]+)?")


class AssetManifestError(ValueError):
    """Raised when a Today in AI image asset manifest is incomplete or unsafe."""


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require_object(value: object, label: str) -> dict:
    if not isinstance(value, dict):
        raise AssetManifestError(f"{label} must be an object")
    return value


def require_text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise AssetManifestError(f"{label} must be a non-empty string")
    return value.strip()


def require_https(value: object, label: str) -> str:
    url = require_text(value, label)
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.netloc:
        raise AssetManifestError(f"{label} must be an https URL")
    return url


def resolve_asset(workspace: Path, value: object, label: str) -> tuple[Path, str]:
    raw = require_text(value, label)
    relative = Path(raw)
    if relative.is_absolute() or ".." in relative.parts:
        raise AssetManifestError(f"{label} must be a workspace-relative path")
    resolved = workspace / relative
    if not resolved.is_file():
        raise AssetManifestError(f"{label} does not exist: {raw}")
    return resolved, raw


def verify_hash(path: Path, value: object, label: str) -> str:
    expected = require_text(value, label).lower()
    if not SHA256_RE.fullmatch(expected):
        raise AssetManifestError(f"{label} must be a lowercase SHA-256 digest")
    actual = sha256(path)
    if actual != expected:
        raise AssetManifestError(
            f"{label} does not match {path}: expected {expected}, got {actual}"
        )
    return actual


def validate_asset_manifest(
    manifest_path: Path,
    workspace: Path = WORKSPACE,
    prompt_path: Path | None = None,
) -> dict:
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise AssetManifestError(f"missing image asset manifest: {manifest_path}") from exc
    except json.JSONDecodeError as exc:
        raise AssetManifestError(f"invalid JSON in {manifest_path}: {exc}") from exc

    schema_version = manifest.get("schema_version")
    if schema_version not in {1, 2}:
        raise AssetManifestError("schema_version must be 1 or 2")

    hook = require_text(manifest.get("hook"), "hook")
    hook_words = WORD_RE.findall(hook)
    if not 2 <= len(hook_words) <= 5:
        raise AssetManifestError(
            f"hook must contain two to five words, found {len(hook_words)}"
        )

    source = require_object(manifest.get("visual_source"), "visual_source")
    source_kind = require_text(source.get("kind"), "visual_source.kind")
    if source_kind not in ALLOWED_SOURCE_KINDS:
        allowed = ", ".join(sorted(ALLOWED_SOURCE_KINDS))
        raise AssetManifestError(
            f"visual_source.kind must be one of: {allowed}"
        )
    source_name = require_text(source.get("name"), "visual_source.name")
    source_family = require_text(source.get("family"), "visual_source.family")
    production_route = source.get("production_route")
    if schema_version == 2:
        production_route = require_text(
            production_route, "visual_source.production_route"
        )
        if production_route not in REFERENCE_ROUTES:
            allowed = ", ".join(sorted(REFERENCE_ROUTES))
            raise AssetManifestError(
                f"visual_source.production_route must be one of: {allowed}"
            )
        if source_kind == "established_meme" and production_route == "generated_original":
            raise AssetManifestError(
                "an established meme cannot use the generated_original route"
            )
    source_path, _ = resolve_asset(
        workspace, source.get("asset_path"), "visual_source.asset_path"
    )
    source_hash = verify_hash(
        source_path, source.get("asset_sha256"), "visual_source.asset_sha256"
    )
    require_text(source.get("usage_note"), "visual_source.usage_note")
    traits = source.get("recognizable_traits")
    if (
        not isinstance(traits, list)
        or len(traits) < 3
        or any(not isinstance(item, str) or not item.strip() for item in traits)
    ):
        raise AssetManifestError(
            "visual_source.recognizable_traits must contain at least three strings"
        )
    if source_kind == "generated_original":
        require_text(
            source.get("why_generated_original"),
            "visual_source.why_generated_original",
        )
    else:
        require_https(source.get("source_page_url"), "visual_source.source_page_url")
        require_https(source.get("asset_url"), "visual_source.asset_url")

    composition = require_object(manifest.get("composition"), "composition")
    composition_fields = {}
    for field in ("main_composition", "subject_pose", "prop_setup", "visual_joke"):
        composition_fields[field] = require_text(
            composition.get(field), f"composition.{field}"
        )

    typography = require_object(manifest.get("typography"), "typography")
    typeface = require_text(typography.get("font"), "typography.font")
    weight = typography.get("weight")
    if not isinstance(weight, int) or weight < 800:
        raise AssetManifestError("typography.weight must be an integer of at least 800")
    for field in (
        "primary_color",
        "accent_color",
        "dominant_phrase",
        "outline_or_shadow",
    ):
        require_text(typography.get(field), f"typography.{field}")

    palette_name = None
    if schema_version == 2:
        palette = require_object(manifest.get("palette"), "palette")
        palette_name = require_text(palette.get("name"), "palette.name")
        if palette_name != "AI Mentorship":
            raise AssetManifestError("palette.name must be AI Mentorship")
        for key, expected in AI_MENTORSHIP_PALETTE.items():
            actual = require_text(palette.get(key), f"palette.{key}")
            if actual.upper() != expected:
                raise AssetManifestError(
                    f"palette.{key} must be exactly {expected}"
                )

    mark = require_object(manifest.get("publication_mark"), "publication_mark")
    mark_path, mark_raw = resolve_asset(
        workspace, mark.get("asset_path"), "publication_mark.asset_path"
    )
    if mark_raw != TODAY_MARK:
        raise AssetManifestError(
            f"publication_mark.asset_path must be exactly {TODAY_MARK}"
        )
    if mark.get("placement") != "bottom-left":
        raise AssetManifestError("publication_mark.placement must be bottom-left")
    if mark.get("treatment") != "fixed-series-badge":
        raise AssetManifestError(
            "publication_mark.treatment must be fixed-series-badge"
        )
    safe_margin = mark.get("safe_margin_px")
    if not isinstance(safe_margin, int) or not 72 <= safe_margin <= 96:
        raise AssetManifestError(
            "publication_mark.safe_margin_px must be between 72 and 96"
        )
    width_percent = mark.get("width_percent")
    if not isinstance(width_percent, (int, float)) or not 10 <= width_percent <= 14:
        raise AssetManifestError(
            "publication_mark.width_percent must be between 10 and 14"
        )
    if schema_version == 2:
        if safe_margin != 84:
            raise AssetManifestError(
                "publication_mark.safe_margin_px must be exactly 84"
            )
        if width_percent != 12:
            raise AssetManifestError(
                "publication_mark.width_percent must be exactly 12"
            )
        for field, expected in BADGE_GEOMETRY.items():
            if mark.get(field) != expected:
                raise AssetManifestError(
                    f"publication_mark.{field} must be exactly {expected}"
                )
        if mark.get("transparent") is not True:
            raise AssetManifestError("publication_mark.transparent must be true")
        if mark.get("applied_by") != "execution/today_in_ai_badge.py":
            raise AssetManifestError(
                "publication_mark.applied_by must be execution/today_in_ai_badge.py"
            )

    composite = require_object(
        manifest.get("deterministic_composite"), "deterministic_composite"
    )
    composite_fields = (
        (
            "exact_text_added_after_generation",
            "badge_added_after_generation",
            "logo_fidelity_verified",
            "badge_zone_reserved",
        )
        if schema_version == 2
        else (
            "text_added_after_generation",
            "logos_added_after_generation",
            "model_prompt_excludes_logos",
        )
    )
    for field in composite_fields:
        if composite.get(field) is not True:
            raise AssetManifestError(
                f"deterministic_composite.{field} must be true"
            )

    logos = manifest.get("logos")
    if not isinstance(logos, list):
        raise AssetManifestError("logos must be an array")
    validated_logos = []
    for index, raw_logo in enumerate(logos):
        logo = require_object(raw_logo, f"logos[{index}]")
        brand = require_text(logo.get("brand"), f"logos[{index}].brand")
        official_url = require_https(
            logo.get("official_source_url"),
            f"logos[{index}].official_source_url",
        )
        logo_path, relative_logo = resolve_asset(
            workspace, logo.get("asset_path"), f"logos[{index}].asset_path"
        )
        logo_hash = verify_hash(
            logo_path, logo.get("asset_sha256"), f"logos[{index}].asset_sha256"
        )
        require_text(logo.get("surface"), f"logos[{index}].surface")
        require_text(logo.get("integration"), f"logos[{index}].integration")
        validated_logos.append(
            {
                "brand": brand,
                "official_source_url": official_url,
                "asset_path": relative_logo,
                "asset_sha256": logo_hash,
            }
        )

    if prompt_path is not None:
        try:
            prompt = prompt_path.read_text(encoding="utf-8").lower()
        except FileNotFoundError as exc:
            raise AssetManifestError(f"missing image prompt: {prompt_path}") from exc
        if schema_version == 2:
            required_constraints = (
                "use the supplied reference images",
                "do not invent or approximate any logo",
                "leave the bottom-left badge area empty",
                "#0b0f0d",
                "#0f583d",
                "#72dfa5",
                "#f7f8f4",
                "#ffffff",
            )
        else:
            required_constraints = ("do not generate or redraw any logo",)
        for required_constraint in required_constraints:
            if required_constraint not in prompt:
                raise AssetManifestError(
                    f"image prompt must include: {required_constraint}"
                )

    return {
        "status": "pass",
        "hook": hook,
        "hook_words": len(hook_words),
        "visual_source_kind": source_kind,
        "visual_source_name": source_name,
        "visual_source_family": source_family,
        "production_route": production_route,
        "visual_source_sha256": source_hash,
        "composition": composition_fields,
        "typeface": typeface,
        "type_weight": weight,
        "palette": palette_name,
        "publication_mark": str(mark_path),
        "badge_geometry": BADGE_GEOMETRY if schema_version == 2 else None,
        "logo_count": len(validated_logos),
        "logos": validated_logos,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--workspace", type=Path, default=WORKSPACE)
    parser.add_argument("--prompt", type=Path)
    args = parser.parse_args()

    try:
        result = validate_asset_manifest(
            args.manifest, workspace=args.workspace, prompt_path=args.prompt
        )
    except AssetManifestError as exc:
        print(json.dumps({"status": "fail", "error": str(exc)}, indent=2))
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
