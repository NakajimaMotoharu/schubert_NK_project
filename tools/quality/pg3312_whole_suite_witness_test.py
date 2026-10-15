import unittest
from pyflakes.api import check
from pg3312_whole_suite_witness import server_source


class SavedSuiteProjectionTest(unittest.TestCase):
    def test_complete_namespace_and_explicit_no_runtime_mutation(self):
        raw = server_source({'source': 'a' * 40, 'wholeSha256': 'b' * 64})
        self.assertEqual(0, check(raw, '<saved suite witness>'))
        self.assertIn('85', raw)
        self.assertIn("v['sourceSnapshotHead']", raw)
        self.assertIn("case.split('(',1)[0]in methods", raw)
        self.assertIn(r"r'\bvoid\s+", raw)
        self.assertNotIn('\b', raw)
        for forbidden in ['subprocess', 'systemctl', 'mvn', 'write_bytes', 'write_text']:
            self.assertNotIn(forbidden, raw)
        compile(raw, '<same3702 original selected suite>', 'exec')


if __name__ == '__main__':
    unittest.main()
