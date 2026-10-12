"""Actual namespace, new host slots and mandatory identity fixture."""
import unittest
import pg1661_completed_unused_dispatch_v3 as p


class NewDispatchTest(unittest.TestCase):
    def test_actual_new_paths_and_fourth_fixture_not_old_namespace(self):
        ns = p.namespace({'actualExit': 0, 'candidateSource': '2741c4546afad6c1e8b6efbd53dfb58144edf7bb', 'manifestSha256': 'a' * 64})
        self.assertEqual('/home/mini/codex/project1/work/pgpt-runs/PG379/pg1659-completed-unused-tools-v3', str(ns['TARGET']))
        self.assertEqual('/var/lib/pgpt-s1-preservation/pg1659-completed-unused-tools-v3', ns['GUEST'])
        self.assertEqual('/home/ubuntu/pg1661-candidate-input-v1', ns['REMOTE'])
        raw = p.source()
        self.assertIn('pg1660-frozen-v1.safe.json', raw)
        self.assertIn('pg1658-owned-recovery-independent-post-v1/manifest.safe.json', raw)
        self.assertIn('pg1661-release-v3.tar', raw)
        self.assertIn("'Pg1660CurrentIdentityTest','Pg1640UnusedStage place'", raw)
        self.assertNotIn('pg1646', raw)
        self.assertNotIn('pg1648', raw)
        self.assertNotIn('systemctl start', raw + p.STAGE)


if __name__ == '__main__':
    unittest.main()
