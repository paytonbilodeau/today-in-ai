import json
from pathlib import Path
import tempfile
import types
import unittest
from unittest import mock

from scripts import fireship_reference_scrape as scrape
from scripts.today_in_ai_assets import AssetManifestError, resolve_asset


class InputSecurityTests(unittest.TestCase):
    def test_asset_symlink_cannot_escape_workspace(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            workspace = base / "workspace"
            workspace.mkdir()
            private = base / "private.txt"
            private.write_text("private fixture")
            (workspace / "asset.txt").symlink_to(private)
            with self.assertRaises(AssetManifestError):
                resolve_asset(workspace, "asset.txt", "Asset")

    def test_regular_asset_inside_workspace_is_allowed(self):
        with tempfile.TemporaryDirectory() as folder:
            workspace = Path(folder)
            asset = workspace / "asset.png"
            asset.write_bytes(b"fixture")
            self.assertEqual((asset.resolve(), "asset.png"), resolve_asset(workspace, "asset.png", "Asset"))

    def test_channel_cannot_be_a_command_option_or_untrusted_host(self):
        for channel in ["--exec=untrusted-command", "file:///private", "https://example.com/channel", "https://user:password@youtube.com/@channel"]:
            with self.subTest(channel=channel), mock.patch.object(scrape, "run") as run:
                with self.assertRaises(ValueError):
                    scrape.flat_catalog(channel, "yt-dlp")
                run.assert_not_called()

    def test_youtube_url_follows_end_of_options(self):
        row = {"id": "abcdefghijk", "title": "Fixture", "view_count": 1, "duration": 120}
        with mock.patch.object(scrape, "run", return_value=types.SimpleNamespace(stdout=json.dumps(row))) as run:
            result = scrape.flat_catalog("https://www.youtube.com/@channel", "yt-dlp")
        self.assertEqual(["--", "https://www.youtube.com/@channel/videos"], run.call_args.args[0][-2:])
        self.assertEqual("abcdefghijk", result[0]["id"])


if __name__ == "__main__":
    unittest.main()
