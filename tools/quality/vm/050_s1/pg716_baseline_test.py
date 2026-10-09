"""Read-only all21, actual702 terminal seal and six old immutable proof trees."""
import ast
import unittest
from pg716_current_baseline import source


class Test(unittest.TestCase):
    def test_complete_current_binding_and_inert_dependency_graph(self):
        raw = source(); ast.parse(raw)
        for value in ('pg716-completed-baseline-v1', 'pg703-bootstrap-final-v4.exit',
                      'dc4d6a6d35ff09ee28e39068ac95887c879d0babe362929873047464e7f0f562',
                      "actor['pid']=='2464638'", "actor['ticks']=='12258069'", 'd420de6553ef48038a40332c37a8b12e',
                      '6b3dd954959c43c1bbac2164ec9d0c6b', 'pg696-native-stop-v1',
                      "require(v[key]==old[key])", '==524', 'require(len(v)==21)',
                      'from pg535_bootstrap_contract import UNIT,normal20',
                      'from pg536_bootstrap_execution_contract import record'):
            self.assertIn(value, raw)
        for name in ('pg664-bootstrap-tools-v1', 'pg664-bootstrap-verify-v1', 'pg664-bootstrap-existing-v1',
                     'pg702-bootstrap-tools-v1', 'pg702-bootstrap-verify-v1', 'pg702-bootstrap-existing-v1'):
            self.assertIn(name, raw)
        for forbidden in ('pg631', '0.1.0-PG631', '36fe7a0b', 'pg715-release-v1', 'daemon-reload', 'reset-failed'):
            self.assertNotIn(forbidden, raw)
        env = {'__file__': __file__, '__name__': 'inert_readonly'}
        exec(compile(raw, '<inert metadata only>', 'exec'), env)
        ast.parse(env['PAYLOAD'])
        self.assertIn("'operationAuthority':False", env['PAYLOAD'])


if __name__ == '__main__': unittest.main()
