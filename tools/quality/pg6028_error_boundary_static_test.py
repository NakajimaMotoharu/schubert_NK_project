import unittest
from collections import Counter
from pyflakes.api import check
import pg6028_error_boundary_static as t


class BoundaryStaticProofTest(unittest.TestCase):
    def test_namespace_and_physical_contract(self):
        names = sorted(k for k in vars(t.engine) if k.isidentifier() and not k.startswith('__') and k != 'main')
        self.assertEqual(0, check('='.join(names)+'=None\nNEW_INTERFACE=validate_diagnostics=None\n'+t.runner_source(), '<complete static namespace>'))
        self.assertIn('originalSelectedOverallExit=1', t.runner_source())
        self.assertIn("'9ecd53b6a1aa5380db0c8420f38323e9d2282871d68f146e636a9d03e088ab6f'", t.runner_source())
        old = {str(i): str(i) for i in range(1664)} | {k: 'old' for k in t.OWNERS}
        new = dict(old) | {k: 'new' for k in t.OWNERS} | {t.NEW_INTERFACE: 'added'}
        self.assertEqual(sorted(t.OWNERS | {t.NEW_INTERFACE}), t.physical_changes(old, new))
        with self.assertRaises(ValueError):
            t.physical_changes(old, dict(new) | {'outside': 'unplanned'})
        new['0'] = 'unrelated'
        with self.assertRaises(ValueError):
            t.physical_changes(old, new)

    def test_no_unrelated_raw_removal_or_suppression(self):
        before = Counter(AvoidCatchingGenericException=20, AvoidInstanceofChecksInCatchClause=8, DoNotUseThreads=10, CloseResource=2)
        after = Counter(AvoidCatchingGenericException=8, AvoidInstanceofChecksInCatchClause=3, DoNotUseThreads=6, CloseResource=2)
        t.expected_rules(before, after)
        after['CloseResource'] -= 1
        with self.assertRaises(ValueError):
            t.expected_rules(before, after)


if __name__ == '__main__':
    unittest.main()
