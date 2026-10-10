import ast
import unittest
from pg1178_canonical_runtime_owner_handoff import source


class CanonicalHandoffTest(unittest.TestCase):
    def test_fixed_owner_once_order_and_preserved_current_closure(self):
        raw = source()
        self.assertTrue('pg1178-canonical-runtime-owner-handoff-v1' in raw)
        self.assertFalse('pg1165-canonical-runtime-owner-handoff-v1' in raw)
        ns = {'__name__': 'data', '__file__': __file__}
        exec(raw, ns)
        s = ns['payload']()
        tree = ast.parse(s)
        for part in ['terminate_once(420168,5004100', 'terminate_once(420139,5003981',
                     '2c8328ea21f976d3ae914ef584a8a6454f56f73568a90ff3191f38299e40fc1f',
                     'zz-pg1160-once-resume.conf', 'canonical_configuration(',
                     'fa4551d834910cac50c0292d04405b0ec512dc984079969a50ccc3f9c2fb1f8b',
                     '0ab4c85f987a6c25670389e575132f7a9bc967b052390b3541651f2e03878a99']:
            self.assertTrue(part in s, part)
        self.assertEqual(sum(isinstance(n, ast.FunctionDef) and n.name == 'current'
                             for n in tree.body), 1)
        self.assertLess(s.index('terminate_once(420168'), s.index('terminate_once(420139'))
        for forbidden in ['systemctl stop', 'systemctl start', 'daemon-reload']:
            self.assertFalse(forbidden in s, forbidden)
        module = ast.Module(body=[n for n in tree.body if not isinstance(n, (ast.FunctionDef, ast.ClassDef))], type_ignores=[])
        stores = [n.id for n in ast.walk(module) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store)]
        for name in ['before', 'NATIVE_FILES', 'CURRENT', 'PROVEN']:
            self.assertEqual(stores.count(name), 1, name)


if __name__ == '__main__':
    unittest.main()
