import unittest
from unittest.mock import patch
from pyflakes.api import check
import pg5984_web_form_selected_v2 as t


class NodeEnvironmentRegressionTest(unittest.TestCase):
    def test_fixed_hash_version_and_path_resolution(self):
        with patch.object(t, 'sha', return_value=t.NODE_SHA), patch.object(t.shutil, 'which', return_value=str(t.NODE)), patch.object(t.subprocess, 'check_output', return_value='v24.19.0\n'):
            self.assertTrue(t.node_environment().startswith(str(t.NODE.parent)+':'))
            with patch.object(t, 'sha', return_value='wrong'), self.assertRaises(ValueError):
                t.node_environment()
            with patch.object(t.shutil, 'which', return_value='/foreign/node'), self.assertRaises(ValueError):
                t.node_environment()
            with patch.object(t.subprocess, 'check_output', return_value='v1\n'), self.assertRaises(ValueError):
                t.node_environment()

    def test_actual_runner_namespace_fixed_source_and_node(self):
        raw = t.runner_source(); names = sorted(k for k in vars(t.previous.previous.engine) if k.isidentifier() and not k.startswith('__') and k != 'main')
        self.assertEqual(0, check('='.join(names)+'=None\nSOURCE=NODE_PATH=NODE_SHA=COUNTS=None\n'+raw, '<pure Nodefixed921>'))
        self.assertIn('head=SOURCE', raw); self.assertIn('os.pathsep+NODE_PATH', raw)
        self.assertIn('043d226d79e10e0d2696adca50d949892ded3dc1ab5e73d485aa4326eca31836', raw)


if __name__ == '__main__':
    unittest.main()
