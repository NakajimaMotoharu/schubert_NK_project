"""Definition-only preflight; imports and compilation never start a production job."""
import ast
import unittest
import pg6112_http_owner_selected as subject


class Definition(unittest.TestCase):
    def test_exact_three_owners_and_declarations(self):
        cases, counts = subject.inventory()
        self.assertEqual((1939, 318), (sum(counts.values()), len(counts)))
        self.assertEqual(6, len(subject.PATHS))
        self.assertEqual(3, sum(map(len, subject.OWNERS.values())))
        source = subject.runner_source()
        ast.parse(source)
        self.assertIn('done=done and target100', source)
        self.assertIn('NODE_PATH', source)
        self.assertNotIn('failed-cohort', source)


if __name__ == '__main__':
    unittest.main()
