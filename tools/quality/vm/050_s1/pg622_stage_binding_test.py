"""Independent closed stage source/current/tenUnit/future path, never runs guest actions."""
import ast
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parent


def constant(name):
    tree=ast.parse((ROOT/'pg622_stage_candidate.py').read_text())
    node=next(n for n in tree.body if isinstance(n,ast.Assign)
              and any(isinstance(t,ast.Name)and t.id==name for t in n.targets))
    return ast.literal_eval(node.value)


class StageBinding(unittest.TestCase):
    def test_complete_actual_signed_source_and_existing_current_are_distinct(self):
        self.assertEqual('72fb7440697ee1048a5c0145055dc1cc3c577914',constant('SOURCE'))
        self.assertEqual('4a2c35463b37956632b6586dfe18f07320777ea863696b25c1e14e913dd3fa1e',constant('DIGEST'))
        payload=constant('PAYLOAD');tree=ast.parse(payload)
        units=next(ast.literal_eval(n.value)for n in tree.body if isinstance(n,ast.Assign)
                   and any(isinstance(t,ast.Name)and t.id=='units'for t in n.targets))
        self.assertEqual(('caddy.service','schubert-nk-web.service','schubert-nk-api.service',
                         'schubert-nk-cleanup.service','schubert-nk-inbox-inspector.service',
                         'schubert-nk-expiry-cleanup.service','schubert-nk-backup.service',
                         'artemis.service','schubert-nk-morning-controller.service',
                         'schubert-nk-bootstrap-admin.service'),units)
        for value in ('0.1.0-PG600','0.1.0-PG621','cc9ed874-7f4f-450e-a188-8de1e42c8441',
                      'a6342b8a764565cdfea256a781029d419888c7b58c0c3f9b00685e30feaa786f',
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
