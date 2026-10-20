import unittest
import pg6052_expiry_combined_selected as t


class OrdinaryFixtureDefinitionTest(unittest.TestCase):
    def test_whole_definition_no_held_operational_actions_and_exact_guard_inventory(self):
        raw = t.runner_source(13, 8)
        for prohibited in ('systemctl', 'qemu', 'sudo', '/opt/schubert-nk/current', '--resume', '--recover'):
            self.assertNotIn(prohibited, raw)
        cases, counts = t.inventory('green')
        self.assertEqual(set(cases), set(t.engine.MODULES))
        self.assertEqual(16, len(counts))
        self.assertEqual(3, counts[t.engine.PACKAGE+'batch.repository.ExpiryAuditResourceFailureTest'])
        self.assertIn(t.engine.PACKAGE+'batch.file.CleanupExpiryExecutionTest', counts)
        self.assertIn("'mavenActualExit'", raw)
        self.assertIn('len(physical) == 1667', __import__('ast').unparse(__import__('ast').parse(raw)))


if __name__ == '__main__':
    unittest.main()
