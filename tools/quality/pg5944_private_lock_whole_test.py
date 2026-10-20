import ast
import unittest
from pyflakes.api import check
import pg5944_private_lock_whole as t
import pg5944_whole_observation as o


class PrivateLockWholeDefinitionTest(unittest.TestCase):
    def test_generated_namespace_exact_inventory_and_original_observation(self):
        raw = t.server_source(t.SOURCE, 'a'*64)
        self.assertEqual(0, check(raw, '<pure generated source fixture>'))
        values = [n.value for n in ast.walk(ast.parse(raw)) if isinstance(n, ast.Constant)]
        for n in (3973, 592, 1666):
            self.assertIn(n, values)
        self.assertIn('PG5944-six-v1', raw); self.assertNotIn('PG5926', raw)
        driver = t.driver_source({}); self.assertIn(t.SLOT, driver)
        self.assertEqual(0, check('import hashlib,json,os,subprocess\nROOT=W=SOURCE=LABEL=run=copy=server_source=None\n'+driver, '<pure operator fixture>'))
        observed = o.observer_source(dict(source=t.SOURCE, tests=3973, suites=592, mainClasses=1666, archiveSha256='a'*64))
        self.assertIn('PG5944-six-v1', observed); self.assertNotIn('pg5926', observed)


if __name__ == '__main__':
    unittest.main()
