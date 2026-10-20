import unittest
from pyflakes.api import check
import pg6034_corrected_boundary_static as t


class CorrectedBoundaryStaticTest(unittest.TestCase):
    def test_full_namespace_current_zero_gate_only(self):
        names = sorted(k for k in vars(t.previous.engine) if k.isidentifier() and not k.startswith('__') and k != 'main')
        raw = t.runner_source()
        self.assertEqual(0, check('='.join(names)+'=None\nNEW_INTERFACE=validate_diagnostics=None\n'+raw, '<corrected complete static namespace>'))
        self.assertIn('originalSelectedOverallExit=0', raw)
        self.assertNotIn("'9ecd53b6", raw)
        t.expected_rules(dict(AvoidCatchingGenericException=12, AvoidInstanceofChecksInCatchClause=7, DoNotUseThreads=5), dict(AvoidCatchingGenericException=2, AvoidInstanceofChecksInCatchClause=2, DoNotUseThreads=1))
        with self.assertRaises(ValueError):
            t.expected_rules(dict(AvoidCatchingGenericException=12, AvoidInstanceofChecksInCatchClause=7, DoNotUseThreads=5), dict(AvoidCatchingGenericException=0, AvoidInstanceofChecksInCatchClause=2, DoNotUseThreads=1))


if __name__ == '__main__':
    unittest.main()
