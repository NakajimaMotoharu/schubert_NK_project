"""Definition only,never starts a fixture job."""
import ast
import unittest
import pg6128_api_management_stop_red as subject


class Definition(unittest.TestCase):
    def test_red_inventory_and_profile(self):
        _, counts = subject.inventory()
        self.assertEqual((20, 9), (sum(counts.values()), len(counts)))
        self.assertEqual(1, counts['dev.codex.schubert.nk.api.bootstrap.ApiManagementStopTest'])
        ast.parse(subject.base_runner(20, 9, target_count=1))


if __name__ == '__main__':
    unittest.main()
