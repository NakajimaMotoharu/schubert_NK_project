"""Literal new/old generation separation; generated source has no app mutation."""
import unittest
import pg1640_completed_unused_candidate_sources as p


class CompletedCandidateSourceTest(unittest.TestCase):
    def test_exact_source_and_original_tuple_not_pending(self):
        v = p.sources('a' * 64)
        java = v['Pg1640UnusedStage.java']
        for literal in ['4d6bcbddb417b76d27e52d5d9640752c300edccf', 'PG1544', '3d69f5af-6bac-46b1-a540-7591c4a79a0d', '0be226b1-bbb7-43d3-aa9e-59d0bda70f9a', 'd28eead2-941c-4b97-9747-1758c0809e29', '2026-10-12T06:48:58.973359Z', 'StartupPermitRecords.State.ISSUED', 'MaintenanceCompletion.Outcome.SUCCESS']:
            self.assertIn(literal, java)
        refs = v['pg1640_native_refs.py']
        for literal in ['2741c4546afad6c1e8b6efbd53dfb58144edf7bb', '0.1.0-PG1638', 'a' * 64, 'pg1641-completed-current-before-v2/before.private.json', p.BEFORE]:
            self.assertIn(literal, refs)
        self.assertNotIn("after['native']", refs)
        for name, raw in v.items():
            for old in ['0.1.0-PG1068', '0.1.0-PG1292', 'cbca8738', '9f651096', '27accac0', 'systemctl start', 'systemctl stop', 'daemon-reload', 'CANONICAL_INVALID']:
                self.assertNotIn(old, raw, name)
        for bad in [None, 'x' * 64, 'a' * 63, True]:
            with self.assertRaises(ValueError):
                p.sources(bad)


if __name__ == '__main__':
    unittest.main()
