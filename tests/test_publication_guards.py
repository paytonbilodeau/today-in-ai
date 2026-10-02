import copy
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import social_publisher as publisher
from scripts.today_in_ai_prepare import manifest


class PublicationGuardTests(unittest.TestCase):
    def fixture(self, root):
        image = root / 'final.png'
        image.write_bytes(b'local image fixture')
        return manifest('Complete link-free edition.\n', image, 'x')

    def test_complete_copy_remains_one_x_value(self):
        with tempfile.TemporaryDirectory() as temporary:
            value = self.fixture(Path(temporary))
            value['targets']['x']['caption'] = 'A complete explanation. ' * 100
            self.assertTrue(publisher.validate_manifest(value)['ok'])
            payload, _ = publisher.render_postiz_payload(
                value, {'postiz': {'x': 'fixture-integration'}},
                {'images': [{'id': 'fixture-image', 'path': 'https://example.com/image.png'}]},
                mode='draft',
            )
            self.assertEqual(len(payload['posts']), 1)
            self.assertEqual(len(payload['posts'][0]['value']), 1)
            self.assertEqual(payload['posts'][0]['value'][0]['content'], value['targets']['x']['caption'])

    def test_thread_is_rejected_by_validation_and_render(self):
        with tempfile.TemporaryDirectory() as temporary:
            value = self.fixture(Path(temporary))
            for policy in ('thread', None):
                target = copy.deepcopy(value)
                target['targets']['x']['thread_policy'] = policy
                self.assertFalse(publisher.validate_manifest(target)['ok'])
                with self.assertRaises(publisher.PublisherError):
                    publisher.render_postiz_payload(target, {'postiz': {'x': 'fixture'}}, {}, mode='draft')

    def test_browser_route_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            value = self.fixture(Path(temporary))
            value['targets']['x']['method'] = 'browser'
            self.assertFalse(publisher.validate_manifest(value)['ok'])

    def test_multiple_images_are_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            value = self.fixture(Path(temporary))
            value['media']['images'] *= 2
            self.assertFalse(publisher.validate_manifest(value)['ok'])

    def test_x_and_linkedin_readiness_does_not_require_other_platforms(self):
        with patch.object(Path, 'exists', return_value=True), \
             patch.object(publisher, 'load_account_map', return_value={'postiz': {'x': 'fixture-x', 'linkedin': 'fixture-linkedin'}}), \
             patch.object(publisher, 'run_postiz', return_value=subprocess.CompletedProcess([], 0, 'Credentials are valid', '')):
            result = publisher.doctor(online=True)
            self.assertTrue(result['postiz_today_in_ai_ready'])

    def test_missing_x_alias_fails_readiness(self):
        with patch.object(Path, 'exists', return_value=True), \
             patch.object(publisher, 'load_account_map', return_value={'postiz': {'linkedin': 'fixture-linkedin'}}), \
             patch.object(publisher, 'run_postiz') as run:
            result = publisher.doctor(online=True)
            self.assertFalse(result['postiz_today_in_ai_ready'])
            run.assert_not_called()

    def test_uncertain_upload_is_journaled_and_blocks_forced_retry(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            value = self.fixture(root)
            path = root / 'manifest.json'
            path.write_text(json.dumps(value))
            journals = root / 'receipts'
            calls = []

            def run(arguments):
                calls.append(arguments)
                if arguments[0] == 'auth:status':
                    return subprocess.CompletedProcess([], 0, 'Credentials are valid', '')
                journal = list(journals.glob('*.json'))
                self.assertEqual(len(journal), 1)
                self.assertTrue(json.loads(journal[0].read_text())['mutation_started'])
                raise publisher.PublisherError('Fixture upload timed out')

            with patch.object(publisher, 'RECEIPTS_DIR', journals), \
                 patch.object(publisher, 'load_account_map', return_value={'postiz': {'x': 'fixture'}}), \
                 patch.object(publisher, 'run_postiz', side_effect=run):
                with self.assertRaisesRegex(publisher.PublisherError, 'uncertain'):
                    publisher.submit_manifest(path, 'now', True, 'PUBLISH', False)
                record = json.loads(next(journals.glob('*.json')).read_text())
                self.assertEqual(record['status'], 'uncertain')
                previous_calls = len(calls)
                with self.assertRaisesRegex(publisher.PublisherError, 'journal blocks retry'):
                    publisher.submit_manifest(path, 'now', True, 'PUBLISH', True)
                self.assertEqual(len(calls), previous_calls)

    def test_fingerprint_tracks_image_bytes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            value = self.fixture(root)
            before = publisher.canonical_fingerprint(value)
            (root / 'final.png').write_bytes(b'another image fixture')
            self.assertNotEqual(before, publisher.canonical_fingerprint(value))


if __name__ == '__main__':
    unittest.main()
