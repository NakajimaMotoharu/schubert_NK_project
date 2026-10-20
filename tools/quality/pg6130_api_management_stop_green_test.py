import ast
import unittest
import pg6130_api_management_stop_green as subject


class Definition(unittest.TestCase):
    def test_four_cases_and_strict_actual_target_gate(self):
        _, counts = subject.inventory()
        self.assertEqual((23, 9), (sum(counts.values()), len(counts)))
        self.assertEqual(4, counts['dev.codex.schubert.nk.api.bootstrap.ApiManagementStopTest'])
        source = subject.runner_source()
        ast.parse(source)
        self.assertIn('done=done and target100', source)


if __name__ == '__main__':
    unittest.main()
