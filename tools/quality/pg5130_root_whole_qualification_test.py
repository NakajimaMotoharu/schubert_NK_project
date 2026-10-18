"""Literal independent Main deltas and required current/prior case counts; no remote actions."""
import inspect
import unittest
from pyflakes.api import check, checkPath
import pg5130_root_whole_qualification as role


class RootWholeQualification(unittest.TestCase):
    def inventories(self):
        old = {'unchanged:' + str(i): 'a' * 64 for i in range(1648)}
        old.update({k:'b' * 64 for k in role.MODIFIED})
        new = {**old, **{k:'c' * 64 for k in role.ADDITIONS}}
        new.update({k:'d' * 64 for k in role.MODIFIED})
        return old, new

    def test_exact_two_outer_and_four_added_with_1648_unchanged(self):
        self.assertEqual(len(role.MODIFIED), 2); self.assertEqual(len(role.ADDITIONS), 4)
        old, new = self.inventories()
        rows, kept = role.physical_difference(old, new, new)
        self.assertEqual(kept, 1648); self.assertEqual(len(rows), 6)
        self.assertEqual(sum(row['action'] == 'ADDED_NATIVE_BINDING' for row in rows), 1)
        for target in role.ADDITIONS:
            missing = dict(new); del missing[target]
            with self.assertRaises(ValueError): role.physical_difference(old, missing, missing)
        drift = dict(new); drift['unchanged:0'] = 'f' * 64
        with self.assertRaises(ValueError): role.physical_difference(old, drift, drift)
        with self.assertRaises(ValueError): role.physical_difference(old, new, old)
        bad = dict(new); bad['unchanged:0'] = True
        with self.assertRaises(ValueError): role.physical_difference(old, bad, bad)

    def test_actual23_new_case_identities_and_full_standalone_namespace(self):
        values = role.added_cases()
        self.assertEqual(len(values), 23); self.assertEqual(len(set(values)), 23)
        raw = role.qualifier_source()
        self.assertIn('len(oldcases) == 3791', raw)
        self.assertIn('len(additions) == 23', raw)
        self.assertIn('len(cases) == 3814', raw)
        self.assertIn('== 556', raw)
        self.assertIn("'mainClasses': 1654", raw)
        self.assertIn("old = base / 'runs/PG4968-six-v1'", raw)
        self.assertIn("out = base / 'runs/PG5128-six-v1'", raw)
        complete = ('import json\nMODIFIED=set()\nADDITIONS=set()\n' + inspect.getsource(role.physical_difference) + '\n' + raw)
        self.assertEqual(0, check(complete, '<complete definitions only>'))
        for path in (role.__file__, __file__): self.assertEqual(0, checkPath(path))


if __name__ == '__main__':
    unittest.main()
