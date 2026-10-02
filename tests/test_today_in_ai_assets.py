import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts.today_in_ai_assets import (
    AssetManifestError,
    TODAY_MARK,
    validate_asset_manifest,
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class TodayInAIAssetManifestTests(unittest.TestCase):
    def build_fixture(self, root: Path) -> tuple[Path, Path]:
        source = root / "today-in-ai/images/2026-07-29/assets/meme.jpg"
        logo = root / "today-in-ai/images/2026-07-29/assets/logo.png"
        mark = root / TODAY_MARK
        for path, contents in (
            (source, b"recognizable meme fixture"),
            (logo, b"official logo fixture"),
            (mark, b"today in ai fixture"),
        ):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(contents)

        manifest = {
            "schema_version": 2,
            "hook": "AI READ THE ROOM",
            "visual_source": {
                "kind": "established_meme",
                "production_route": "reference_generation",
                "name": "Established Meme",
                "family": "reaction close-up",
                "source_page_url": "https://example.com/source",
                "asset_url": "https://example.com/asset.jpg",
                "asset_path": str(source.relative_to(root)),
                "asset_sha256": digest(source),
                "usage_note": "Transformed editorial use with source recorded.",
                "recognizable_traits": [
                    "tight crop",
                    "side-eye expression",
                    "single prop",
                ],
                "why_generated_original": "",
            },
            "composition": {
                "main_composition": "One reaction cutout opposite the hook",
                "subject_pose": "Subject turns toward one prop",
                "prop_setup": "One oversized folder",
                "visual_joke": "The folder knows too much",
            },
            "typography": {
                "font": "Instrument Sans ExtraBold",
                "weight": 800,
                "primary_color": "#FFFFFF",
                "accent_color": "#72DFA5",
                "dominant_phrase": "READ THE ROOM",
                "outline_or_shadow": "Six pixel dark outline",
            },
            "palette": {
                "name": "AI Mentorship",
                "jet_black": "#0B0F0D",
                "old_money_green": "#0F583D",
                "mint_green": "#72DFA5",
                "warm_paper": "#F7F8F4",
                "white": "#FFFFFF",
            },
            "publication_mark": {
                "asset_path": TODAY_MARK,
                "placement": "bottom-left",
                "treatment": "fixed-series-badge",
                "safe_margin_px": 84,
                "width_percent": 12,
                "canvas_width_px": 1920,
                "canvas_height_px": 1080,
                "left_px": 84,
                "bottom_px": 84,
                "width_px": 230,
                "transparent": True,
                "applied_by": "execution/today_in_ai_badge.py",
            },
            "deterministic_composite": {
                "exact_text_added_after_generation": False,
                "exact_text_integrated_in_generation": True,
                "badge_added_after_generation": True,
                "logo_fidelity_verified": True,
                "badge_zone_reserved": True,
            },
            "logos": [
                {
                    "brand": "Example",
                    "official_source_url": "https://example.com/brand",
                    "asset_path": str(logo.relative_to(root)),
                    "asset_sha256": digest(logo),
                    "surface": "Front-facing device display",
                    "integration": "Match perspective, light, grain, and occlusion.",
                }
            ],
        }
        manifest_path = root / "today-in-ai/editions/2026-07-29/image-assets.json"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        prompt_path = manifest_path.with_name("image-prompt.txt")
        prompt_path.write_text(
            "Render the exact hook AI READ THE ROOM. Use the supplied reference images. "
            "Do not invent or approximate any logo. "
            "Leave the bottom-left badge area empty. Use #0B0F0D, #0F583D, #72DFA5, "
            "#F7F8F4, and #FFFFFF.",
            encoding="utf-8",
        )
        return manifest_path, prompt_path

    def test_valid_manifest_passes(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            manifest, prompt = self.build_fixture(root)
            result = validate_asset_manifest(manifest, root, prompt)
            self.assertEqual(result["status"], "pass")
            self.assertEqual(result["logo_count"], 1)
            self.assertEqual(result["hook_words"], 4)

    def test_publication_mark_must_be_fixed_bottom_left(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            manifest, prompt = self.build_fixture(root)
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            payload["publication_mark"]["placement"] = "in-scene-sign"
            manifest.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(AssetManifestError, "bottom-left"):
                validate_asset_manifest(manifest, root, prompt)

    def test_prompt_must_forbid_generated_logos(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            manifest, prompt = self.build_fixture(root)
            prompt.write_text("Create a clean background.", encoding="utf-8")
            with self.assertRaisesRegex(AssetManifestError, "supplied reference"):
                validate_asset_manifest(manifest, root, prompt)

    def test_v2_publication_mark_uses_locked_geometry(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            manifest, prompt = self.build_fixture(root)
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            payload["publication_mark"]["width_px"] = 240
            manifest.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(AssetManifestError, "exactly 230"):
                validate_asset_manifest(manifest, root, prompt)

    def test_v2_palette_is_exact(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            manifest, prompt = self.build_fixture(root)
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            payload["palette"]["mint_green"] = "#00FF00"
            manifest.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(AssetManifestError, "#72DFA5"):
                validate_asset_manifest(manifest, root, prompt)

    def test_v2_requires_exactly_one_text_route(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            manifest, prompt = self.build_fixture(root)
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            payload["deterministic_composite"]["exact_text_integrated_in_generation"] = False
            manifest.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(AssetManifestError, "exactly one text route"):
                validate_asset_manifest(manifest, root, prompt)

    def build_styled_fixture(self, root: Path) -> tuple[Path, Path]:
        manifest, prompt = self.build_fixture(root)
        payload = json.loads(manifest.read_text())
        payload["schema_version"] = 3
        payload["publication_mark"] = {
            "asset_path": TODAY_MARK,
            "asset_sha256": digest(root / TODAY_MARK),
            "treatment": "style-matched-in-scene",
            "surface": "Engraved front face of the paper model",
            "style_treatment": "Paper texture and pencil contours preserve the mark's structure",
        }
        payload.pop("deterministic_composite")
        payload["generation"] = dict.fromkeys((
            "official_references_supplied",
            "exact_text_integrated_in_generation",
            "logos_styled_in_generation",
            "logo_structure_verified",
            "logo_style_match_verified",
            "natural_surface_integration_verified",
            "no_flat_logo_overlays",
            "full_size_and_phone_size_verified",
        ), True)
        manifest.write_text(json.dumps(payload))
        prompt.write_text(
            "AI READ THE ROOM. Use the supplied reference images. "
            "Preserve exact recognizable logo structure. "
            "Render every logo in the same image style. "
            "Integrate the Today in AI mark into the scene. No flat logo overlays. "
            "Use #0B0F0D, #0F583D, #72DFA5, #F7F8F4, and #FFFFFF."
        )
        return manifest, prompt

    def test_styled_mark_passes_without_fixed_badge_geometry(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            manifest, prompt = self.build_styled_fixture(root)
            result = validate_asset_manifest(manifest, root, prompt)
            self.assertEqual(result["status"], "pass")
            self.assertIsNone(result["badge_geometry"])

    def test_styled_mark_requires_each_visual_and_reference_check(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            manifest, prompt = self.build_styled_fixture(root)
            original = json.loads(manifest.read_text())
            for field in original["generation"]:
                with self.subTest(field=field):
                    payload = json.loads(json.dumps(original))
                    payload["generation"][field] = False
                    manifest.write_text(json.dumps(payload))
                    with self.assertRaisesRegex(AssetManifestError, field):
                        validate_asset_manifest(manifest, root, prompt)

    def test_styled_mark_rejects_a_fixed_overlay(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            manifest, prompt = self.build_styled_fixture(root)
            payload = json.loads(manifest.read_text())
            payload["publication_mark"]["treatment"] = "fixed-series-badge"
            manifest.write_text(json.dumps(payload))
            with self.assertRaisesRegex(AssetManifestError, "style-matched-in-scene"):
                validate_asset_manifest(manifest, root, prompt)

    def test_styled_mark_rejects_changed_official_reference(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            manifest, prompt = self.build_styled_fixture(root)
            (root / TODAY_MARK).write_bytes(b"different logo")
            with self.assertRaises(AssetManifestError):
                validate_asset_manifest(manifest, root, prompt)


if __name__ == "__main__":
    unittest.main()
