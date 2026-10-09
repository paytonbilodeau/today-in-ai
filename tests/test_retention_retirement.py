import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/today_in_ai_retention.py'
spec = importlib.util.spec_from_file_location('retention', SCRIPT)
retention = importlib.util.module_from_spec(spec)
spec.loader.exec_module(retention)


class RetiredCleanupTests(unittest.TestCase):
    def test_legacy_cli_preserves_old_delivery_and_state(self):
        for apply in (False, True):
            with self.subTest(apply=apply), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                old = root / 'delivery/Today in AI - 2020-01-01/final.txt'
                old.parent.mkdir(parents=True)
                old.write_bytes(b'keep this delivery')
                state = root / 'state.json'
                state.write_bytes(b'{"last_cleanup_date":"2020-01-01"}\n')
                before = state.read_bytes()
                command = [sys.executable, str(SCRIPT), '--date', '2026-10-09',
                           '--delivery-root', str(root / 'delivery'),
                           '--state-file', str(state), '--trash-root', str(root / 'trash')]
                if apply:
                    command.append('--apply')
                result = subprocess.run(command, check=True, capture_output=True, text=True)
                self.assertEqual(json.loads(result.stdout)['status'], 'retired_age_only_cleanup')
                self.assertEqual(json.loads(result.stdout)['moved'], [])
                self.assertEqual(old.read_bytes(), b'keep this delivery')
                self.assertEqual(state.read_bytes(), before)
                self.assertFalse((root / 'trash').exists())

    def test_direct_apply_rejects_without_creating_trash(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / 'source.txt'
            source.write_bytes(b'keep')
            with self.assertRaisesRegex(RuntimeError, 'retired'):
                retention.apply_retention({'trash': [str(source)]}, root / 'trash')
            self.assertEqual(source.read_bytes(), b'keep')
            self.assertFalse((root / 'trash').exists())


if __name__ == '__main__':
    unittest.main()
