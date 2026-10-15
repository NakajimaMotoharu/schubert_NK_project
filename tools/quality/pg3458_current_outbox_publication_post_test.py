import json
import unittest
from pg1446_current_cold_stage import W
import pg3458_current_outbox_publication_post as post


class ExactPublicationObserver(unittest.TestCase):
    def test_seven_phase_and_data_native_projection_explicit(self):
        p = W / 'pg3430-current-a9-readonly-before-v1'
        raw = (p / 'payload.private.py').read_text()
        receipt = json.loads((p / 'manifest.safe.json').read_bytes())
        fixed = {'actualExit': 0, 'fileHashes': {}}
        result = post.compose(raw, receipt, fixed, post.role.ro.role.BOM)
        for marker in ['pg3450_ordinary_publication_contract', post.role.SAVE, post.SLOT,
                       '0.1.0-PG3420', post.role.production(), post.role.BEFORE,
                       'historical_native', 'require(native==historical_native)',
                       "tuple(dict.fromkeys(phase", "after['unitFilesActual']==old_after['unitFilesActual']",
                       'pg3432-current-a9-before-view-v2/before.private.json']:
            self.assertIn(marker, result)
        # Original sealed current proof stays a9, never rewritten as new parent evidence.
        self.assertIn("original['source']=='" + post.role.CURRENT + "'", result)
        for changes in [{'productionSource': '0' * 40}, {'actualExit': False},
                        {'payloadSha256': '0' * 64}]:
            with self.assertRaises(ValueError):
                post.compose(raw, {**receipt, **changes}, fixed, post.role.ro.role.BOM)
        with self.assertRaises(ValueError):
            post.compose(raw, receipt, {'actualExit': False, 'fileHashes': {}}, post.role.ro.role.BOM)


if __name__ == '__main__':
    unittest.main()
