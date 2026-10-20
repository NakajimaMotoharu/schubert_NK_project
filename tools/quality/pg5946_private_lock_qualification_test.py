import ast
import unittest
from pyflakes.api import check
import pg5946_private_lock_qualification as t


class OriginalPrivateLockReaderTest(unittest.TestCase):
    def test_exact_generated_definitions_without_pt_or_runtime_calls(self):
        self.assertEqual([], t.added_cases()); self.assertEqual(54, len(t.physical_kinds()))
        raw = t.emitted({}); self.assertEqual(0, check(raw, '<generated fixture>'))
        self.assertIn('source-full-PG5944', raw); self.assertNotIn('source-full-PG5926', raw)
        self.assertIn('privateLock34TargetFour100', raw)
        for forbidden in ('Popen', 'subprocess.run', 'systemctl', 'socket.connect'):
            self.assertNotIn(forbidden, raw)
        values = [n.value for n in ast.walk(ast.parse(raw)) if isinstance(n, ast.Constant)]
        for number in (3973, 592, 1666, 1612, 54, 34):
            self.assertIn(number, values)
        operator = t.operator_source()
        self.assertEqual(0, check('import hashlib,json,os,subprocess\nW=ORIGINAL=SOURCE=ROOT=BASE=SLOT=TARGETS=physical_difference=added_cases=emitted=run=copy=None\n'+operator, '<reader operator fixture>'))


if __name__ == '__main__':
    unittest.main()
