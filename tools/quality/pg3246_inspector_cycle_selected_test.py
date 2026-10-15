"""Fixed current qualification source and all Inspector cases, no duplicate Main."""
import unittest
from pyflakes.api import check
from pg3246_inspector_cycle_selected import server, METHOD


class InspectorScope(unittest.TestCase):
    def test_complete_namespace_and_single_new_required_case(self):
        raw = server('cycle')
        self.assertEqual(0, check('INPUT={}\n' + raw, '<four Inspector cases>'))
        for value in ['source-full-PG3204', 'platform.InspectorUnitCycleTest', 'platform/MorningBackupUnitCycle', METHOD, "'mainRecompiled':False", "'nativeImported':False"]:
            self.assertIn(value, raw)
        self.assertNotIn('platform.MorningBackupUnitCycleTest', raw)
        self.assertNotIn('bucycle3244001', raw)


if __name__ == '__main__':
    unittest.main()
