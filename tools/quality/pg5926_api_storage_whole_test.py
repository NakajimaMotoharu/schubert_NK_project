import ast
import unittest
import pg5926_api_storage_whole as t
import pg5926_whole_observation as o


class Current3973SourceDefinitionTest(unittest.TestCase):
    def test_full_generated_namespaces_and_frozen_inventory_no_runtime_call(self):
        raw = t.server_source(t.SOURCE, 'a' * 64)
        values = [n.value for n in ast.walk(ast.parse(raw)) if isinstance(n, ast.Constant)]
        for n in (3973, 592, 1666):
            self.assertIn(n, values)
        self.assertIn('source-full-PG5926', raw); self.assertNotIn('PG5886', raw)
        self.assertNotIn('failIfNoTests=false', raw)
        driver = t.driver_source({})
        self.assertIn(t.SLOT, driver)
        self.assertIn("'tests': 3973, 'suites': 592, 'mainClasses': 1666", driver)
        self.assertEqual(9, len(t.MODIFIED))
        observed = o.observer_source(dict(source=t.SOURCE, tests=3973, suites=592, mainClasses=1666, archiveSha256='a'*64))
        self.assertIn('PG5926-six-v1', observed); self.assertNotIn('PG5754', observed)


if __name__ == '__main__':
    unittest.main()
