"""Independent closed stage source/current/tenUnit/future path, never runs guest actions."""
import ast
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parent


def constant(name):
    tree=ast.parse((ROOT/'pg632_stage_candidate.py').read_text())
    node=next(n for n in tree.body if isinstance(n,ast.Assign)
              and any(isinstance(t,ast.Name)and t.id==name for t in n.targets))
    return ast.literal_eval(node.value)


class StageBinding(unittest.TestCase):
    def test_complete_actual_signed_source_and_existing_current_are_distinct(self):
        script=(ROOT/'pg632_stage_candidate.py').read_text()
        self.assertIn('from pg601_stage_contract import check_members',script)
        self.assertIn("Path(__file__).parent / 'pg601_stage_contract.py'",script)
        self.assertNotIn('pg632_stage_contract',script)
        self.assertTrue((ROOT/'pg601_stage_contract.py').is_file())
        for value in ('pg632-stage-v1','pg632-release-v1.tar','pg632-candidate-stage-v1'):
            self.assertIn(value,script)
        self.assertNotIn('pg632-stage-v0',script)
        self.assertIn("'run': 'PG632-candidate-stage-v1'",script)
        self.assertNotIn('PG632-candidate-stage-v0',script)
        self.assertEqual('36fe7a0b938489d61d17d49c1c30a6fbbef699d5',constant('SOURCE'))
        self.assertEqual('57a5355d7d0c6a3af7ff2ec619eacee20ee9236916de25e02b95953ffa6aa2fe',constant('DIGEST'))
        payload=constant('PAYLOAD');tree=ast.parse(payload)
        units=next(ast.literal_eval(n.value)for n in tree.body if isinstance(n,ast.Assign)
                   and any(isinstance(t,ast.Name)and t.id=='units'for t in n.targets))
        self.assertEqual(('caddy.service','schubert-nk-web.service','schubert-nk-api.service',
                         'schubert-nk-cleanup.service','schubert-nk-inbox-inspector.service',
                         'schubert-nk-expiry-cleanup.service','schubert-nk-backup.service',
                         'artemis.service','schubert-nk-morning-controller.service',
                         'schubert-nk-bootstrap-admin.service'),units)
        for value in ('0.1.0-PG621','0.1.0-PG631','cc9ed874-7f4f-450e-a188-8de1e42c8441',
                      '4a2c35463b37956632b6586dfe18f07320777ea863696b25c1e14e913dd3fa1e',
                      "'LoadState':'loaded'","'ControlPID':'0'"):
            self.assertIn(value,payload)
        self.assertLess(payload.index('terminal()'),payload.index('root.mkdir'))
        self.assertLess(payload.index("policy['check_members']"),payload.index('tar.extractall'))
        self.assertIn('assert current.readlink()==old',payload)
        self.assertNotIn('systemctl start',payload)
        self.assertNotIn('systemctl stop',payload)
        self.assertNotIn('daemon-reload',payload)
        compile(payload,'<stage readonly-before-copy>','exec')


if __name__=='__main__':unittest.main()
