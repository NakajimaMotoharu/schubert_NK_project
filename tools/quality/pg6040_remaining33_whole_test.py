import ast
import unittest
from pyflakes.api import check
import pg6040_remaining33_whole as t


class Current3976HostWholeTest(unittest.TestCase):
    def test_complete_profile_and_exact_count_replacement(self):
        raw = t.server_source(t.SOURCE, '0'*64)
        self.assertEqual(0, check(raw, '<complete standalone3976>'))
        values = [x.value for x in ast.walk(ast.parse(raw)) if isinstance(x, ast.Constant) and type(x.value) is int]
        self.assertEqual((2, 1, 1), tuple(values.count(n) for n in (3976, 593, 1667)))
        self.assertNotIn(3973, values)
        driver = t.driver_source({'definitionFixtureOnly': True})
        self.assertIn("'tests': 3976, 'suites': 593, 'mainClasses': 1667", driver)
        self.assertNotIn('PG6014', driver)
        self.assertEqual((22, 33), (len(t.plan()['sourcePlans']), t.plan()['selectedDiagnosticConditions']))
        for forbidden in ('systemctl', 'qemu-system', 'sudo ', '--recover', '--resume', '/opt/schubert-nk/current'):
            self.assertNotIn(forbidden, raw)


if __name__ == '__main__':
    unittest.main()
