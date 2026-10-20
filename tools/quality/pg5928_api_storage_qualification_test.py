import ast
import unittest
import pg5928_api_storage_qualification as t


class IndependentCurrent3973DefinitionTest(unittest.TestCase):
    def test_all_namespaces_and_exact_physical_test_inventory(self):
        self.assertEqual([], t.added_cases()); self.assertEqual(16, len(t.PHYSICAL_KINDS))
        raw = t.emitted({}); values = [n.value for n in ast.walk(ast.parse(raw)) if isinstance(n, ast.Constant)]
        for n in (3973, 592, 1666, 1650, 0):
            self.assertIn(n, values)
        self.assertIn('source-full-PG5926', raw); self.assertNotIn('source-full-PG5886', raw)
        self.assertIn('allSeventeenTargetFour100', raw)
        self.assertNotIn('Popen', raw); self.assertNotIn('subprocess.run', raw)
        operator = t.operator_source()
        self.assertIn('PG5886-current3973-cases', operator); self.assertIn('PG5928-qualified-v1', operator)


if __name__ == '__main__':
    unittest.main()
