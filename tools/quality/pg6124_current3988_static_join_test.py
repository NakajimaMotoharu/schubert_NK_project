"""Source-locked definition checks before whole result; never issue tests/jobs."""
import unittest
from collections import Counter
import pg6124_current3988_static_join as subject


class Definition(unittest.TestCase):
    def test_no_missing_or_malformed_whole_hash_can_become_pass(self):
        with self.assertRaises(ValueError):
            subject.reviewed_result('not-hash', 'not-hash')

    def test_only685_strict_pending_and34_explicit_source_rereviews(self):
        old, before, raw, static = subject.inputs()
        rows, prior = subject.strict_pending(old, before, raw, static['allPhysicalMainSha256'])
        self.assertEqual((1311, 685), (len(rows), len(prior)))
        for row in rows:
            if row['findingId'] in prior:
                self.assertEqual('SOURCE_REBOUND_CURRENT_WHOLE_PENDING', row['status'])
                self.assertTrue(row['currentWholeJoinPending'])
                self.assertEqual([], row['currentWholeCaseRefs'])
                self.assertTrue(row['reason'].strip())
        reviews = subject.changed_reviews(old, raw, before, static['allPhysicalMainSha256'])
        self.assertEqual(34, len(reviews))
        self.assertEqual(Counter(REQUIRED_CONTRACT=17, FALSE_POSITIVE=2, CONTEXT_NOT_APPLICABLE=15), Counter(r['status'] for r in reviews))
        self.assertTrue(all(r['reason'].strip() and r['currentWholeJoinPending'] for r in reviews))
        self.assertFalse(any(r['currentWholeCaseRefs'] for r in reviews))


if __name__ == '__main__':
    unittest.main()
