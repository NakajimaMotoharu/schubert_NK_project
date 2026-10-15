"""Exact current whole base, finite two-method presence and no Main rebuild."""
import inspect
import unittest
from pyflakes.api import check
import pg3244_backup_cycle_selected as selected


class SelectedCycle(unittest.TestCase):
    def test_whole_compiler_and_runner_namespace(self):
        raw = selected.server('cycle')
        self.assertEqual(0, check('INPUT={}\n' + raw, '<whole selected cycle>'))
        for literal in ['source-full-PG3204', 'platform.MorningBackupUnitCycleTest', 'platform/MorningBackupUnitCycle', "classes.rglob('MorningBackupUnitCycle*.class')", "require(not mainclasses)", "'mainRecompiled':False", "'vmActions':0", "'nativeImported':False", "'targetClassFour100':all", "not str(p.relative_to(repo)).startswith('dev/codex/schubert/')"] + selected.METHODS:
            self.assertIn(literal, raw)
        self.assertNotIn('repository.CleanupDatabaseSessionTest', raw)
        with self.assertRaises(ValueError): selected.server('other')

    def test_transport_uses_current3694_not_earlier_host_acceptance(self):
        raw = inspect.getsource(selected.main)
        self.assertIn('pg3206-expiry-group-full-qualified-v1', raw)
        self.assertIn("'3694'", raw)
        self.assertEqual(3, len(selected.FILES))


if __name__ == '__main__':
    unittest.main()
