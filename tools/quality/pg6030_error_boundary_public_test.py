import hashlib
import unittest
import pg6030_error_boundary_public as t


class IndependentBoundaryQualificationTest(unittest.TestCase):
    def test_separate_new_identity_from_unchanged_actual_xml(self):
        raw = 'ordinary()'; digest = hashlib.sha256(raw.encode()).hexdigest()
        self.assertEqual(digest, t.original_identity('OldTest', raw, {('OldTest', digest)}))
        with self.assertRaises(ValueError):
            t.original_identity('OldTest', 'other()', {('OldTest', digest)})
        for name in t.NEW_METHODS:
            self.assertEqual(hashlib.sha256(name.encode()).hexdigest(), t.original_identity(t.NEW_TEST, name, set()))
            with self.assertRaises(ValueError):
                t.original_identity(t.NEW_TEST, name+'()', set())
            with self.assertRaises(ValueError):
                t.original_identity(t.NEW_TEST, name, {(t.NEW_TEST, hashlib.sha256(name.encode()).hexdigest())})
        with self.assertRaises(ValueError):
            t.original_identity(t.NEW_TEST, 'undeclared()', set())

    def test_no_missing_counter_can_be_filled_with_zero(self):
        counters = {name: {k: dict(covered=1, missed=0) for k in ('LINE', 'METHOD', 'CLASS', 'BRANCH')} for name in ('batch:A', 'web:B')}
        self.assertTrue(t.four100(counters))
        counters['batch:A']['BRANCH']['missed'] = 1
        self.assertFalse(t.four100(counters))
        del counters['batch:A']['BRANCH']
        self.assertFalse(t.four100(counters))


if __name__ == '__main__':
    unittest.main()
