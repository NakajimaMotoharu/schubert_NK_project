"""Policy-only golden profile/null inventory regressions; no existing run output executed."""
import pathlib
import runpy
import unittest
from unittest.mock import patch

R = pathlib.Path(__file__).resolve().parent


class CollectorProfileContract(unittest.TestCase):
    def test_profile_and_missing_duplicate_labels_reject_before_any_output(self):
        module = runpy.run_path(str(R / 'pg593_collect_full.py'))
        original = (R / 'pg585_collect_full.py').read_text()
        source = module['policy']()
        compile(source, '<profile fixture>', 'exec')
        self.assertIn("run = W / 'pg593-grouped-six-host-v1'", source)
        self.assertIn("'run':'PG593-grouped-six-host-v1'", source)
        self.assertIn('afc470b47a422fb8029c23a96f647889d47a2e9e', source)
        self.assertIn("result['tests']==3447 and result['suites']==511", source)
        self.assertNotIn('pg585-access-reactor-v3', source)
        self.assertNotIn('PG585-access-reactor-v3', source)
        for changed in (original.replace('pg585-access-reactor-v3', 'missing'),
                        original + '\n# pg585-access-reactor-v3\n',
                        original.replace('PG585-access-reactor-v3', 'missing')):
            with patch.object(pathlib.Path, 'read_text', return_value=changed):
                with self.assertRaises(AssertionError):
                    module['policy']()
        for name in ('pg588_collect_selected.py', 'pg589_collect_selected.py',
                     'pg590_collect_selected.py', 'pg592_collect_selected.py'):
            other = runpy.run_path(str(R / name))['policy']()
            compile(other, '<old sealed policy fixture>', 'exec')
            self.assertIn('selectedTests', other)


if __name__ == '__main__':
    unittest.main()
