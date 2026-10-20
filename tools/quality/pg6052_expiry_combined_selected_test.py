import unittest
import pg6052_expiry_combined_selected as t


class OrdinaryFixtureDefinitionTest(unittest.TestCase):
    def test_whole_definition_no_held_operational_actions_and_exact_guard_inventory(self):
        raw = t.runner_source(13, 8)
        for prohibited in ('systemctl', 'qemu', 'sudo', '/opt/schubert-nk/current', '--resume', '--recover'):
            self.assertNotIn(prohibited, raw)
        cases, counts = t.inventory()
        self.assertEqual(set(cases), set(t.engine.MODULES))
        self.assertEqual((13, 8), (sum(counts.values()), len(counts)))
        self.assertIn("'mavenActualExit'", raw)
        self.assertIn('len(physical) == 1667', __import__('ast').unparse(__import__('ast').parse(raw)))


if __name__ == '__main__':
    unittest.main()
