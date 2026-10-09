"""BOOT703001 literal actual witness pins and immutable full21 closure."""
import ast
import unittest
from pg703_final import source


class Test(unittest.TestCase):
    def test_complete_actual_current_scope(self):
        raw = source(); ast.parse(raw)
        for value in ('1d70b8f79fb1aa6c1da796b181948334e2a4a7ae962a0365fb5b0c6750c4fb53',
                      'dc4d6a6d35ff09ee28e39068ac95887c879d0babe362929873047464e7f0f562',
                      'd420de6553ef48038a40332c37a8b12e', "'2464638'", "'12258069'", "'128965'",
                      '122580694582', '122582163571', '0.1.0-PG682', 'pg682-manifest.sig',
                      'len(initial)==21', "initial['currentBootstrapProofs']", '==524',
                      'manager.RefUnit(u)', 'manager.UnrefUnit(u)', 'extra();snapshot();extra();snapshot()',
                      "'newMetadataScopesNormal':True", "'formalAccepted':False"):
            self.assertIn(value, raw)
        for old in ('0.1.0-PG631', '36fe7a0b', '65bfe1da', '2142585', 'signal.pidfd', 'daemon-reload', 'reset-failed'):
            self.assertNotIn(old, raw)
        self.assertIn("not p.name.endswith('.retired.private')", raw)

    def test_vm_signature_matches_actual_stage_not_host_name(self):
        from pg686_stage_candidate import source as stage_source
        env = {}; exec(compile(stage_source(), '<inert stage>', 'exec'), env)
        node = next(n for n in ast.parse(env['PAYLOAD']).body if isinstance(n, ast.Assign)
                    and any(isinstance(t, ast.Name) and t.id == 'sig' for t in n.targets))
        self.assertEqual(ast.literal_eval(node.value.args[0]), '/var/lib/pgpt-s1-preservation/pg682-manifest.sig')
        post = {}; exec(compile(source(), '<inert post>', 'exec'), post)
        self.assertIn("str(base/'pg682-manifest.sig')", post['PAYLOAD'])
        self.assertNotIn('pg682-manifest-v1.sig', post['PAYLOAD'])
        self.assertIn('pg703-bootstrap-final-v4', source())


if __name__ == '__main__': unittest.main()
