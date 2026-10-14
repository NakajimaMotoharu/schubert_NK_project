"""BUG1247/YKT1013 non-target imports and full source namespace; no actual dispatch."""
import importlib
import inspect
import unittest
from pyflakes.api import check
from pg2674_operation_publication_sources import production as fixed_production


class SelectedDependencies(unittest.TestCase):
    def test_fixed_dependency_for_all_new_producers(self):
        expected = '04207efc3ad78bca75942153a90c70985064c988'
        for name, label, launcher in [
            ('pg2732_backup_published_selected', 'PG2732-selected-v1', 'Pg2732BackupPublishedLauncher'),
            ('pg2736_backup_retention_selected', 'PG2736-selected-v2', 'Pg2736BackupRetentionLauncher'),
            ('pg2740_backup_pending_selected', 'PG2740-selected-v1', 'Pg2740BackupPendingLauncher'),
        ]:
            with self.subTest(module=name):
                module=importlib.import_module(name)
                self.assertEqual(expected,module.SOURCE)
                self.assertIs(fixed_production,module.production)
                self.assertIn('from pg2674_operation_publication_sources import production',inspect.getsource(module))
                raw=module.server()
                compile(raw,'<whole selected namespace>','exec')
                self.assertEqual(0,check('INPUT={}\n'+raw,'<whole selected static>'))
                self.assertIn(label,raw)
                self.assertIn(launcher,raw)
                self.assertIn('source-full-PG2694',raw)
                self.assertNotIn('source-full-PG2124',raw)
        for name in ['pg2734_backup_published_qualification','pg2738_backup_retention_qualification']:
            module=importlib.import_module(name)
            self.assertEqual(expected,module.production())
            self.assertIs(fixed_production,module.production)


if __name__=='__main__':unittest.main()
