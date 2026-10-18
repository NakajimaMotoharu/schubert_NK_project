"""BUG1403/YKT1167 estimate revision/hash coupling, no real metric append."""
import hashlib
import unittest
from unittest.mock import patch
import pg998_metrics as metrics


class Revision(unittest.TestCase):
    def test_legacy_default_and_explicit_v4_exact_original_files(self):
        for values, revision, path in [({}, 'PMO-remaining-v3-20261010', metrics.V3),
                ({'costRevision': 'PMO-remaining-v4-20261018'}, 'PMO-remaining-v4-20261018', metrics.V4)]:
            raw = path.read_bytes()
            expected = hashlib.sha256(raw).hexdigest()
            self.assertEqual((revision, expected), metrics.estimate_identity(values))
            self.assertEqual((revision, expected), metrics.estimate_identity({**values, 'estimateRevisionSha256': expected}))
            self.assertEqual(raw, path.read_bytes())

    def test_unknown_mismatch_and_null_refused_before_event_file_open(self):
        for values in [{'costRevision': 'unknown'}, {'costRevision': None},
                       {'costRevision': 'PMO-remaining-v4-20261018', 'estimateRevisionSha256': '0' * 64},
                       {'costRevision': 'PMO-remaining-v4-20261018', 'estimateRevisionSha256': None}]:
            with patch.object(metrics, 'EVENTS') as event:
                with self.assertRaises(ValueError):
                    metrics.append('purefixture', 'CHECKPOINT', values)
            event.open.assert_not_called()


if __name__ == '__main__':
    unittest.main()
