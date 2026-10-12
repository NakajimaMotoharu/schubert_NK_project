"""Actual emitted current closure has no stale actor or reload/start authority."""
import ast
import unittest
from pg1950_reload_pair_once_handoff import payload


class Current(unittest.TestCase):
    def test_emitted_actor_roles_and_single_term(self):
        raw=payload();tree=ast.parse(raw)
        calls=[n for n in ast.walk(tree)if isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id=='terminate']
        self.assertEqual([495760,495729],[n.args[0].value for n in calls])
        self.assertEqual([10125088,10124906],[n.args[1].value for n in calls])
        for old in ['291213','291242','490998','491029','493115','493146','pg1664-current-unused-pair-proof-v1']:
            self.assertNotIn(old,raw)
        self.assertIn("expected['reloadActuallyApplied'] is True",raw)
        self.assertIn('SuccessExitStatus=10',raw)
        self.assertIn('range(9)',raw)
        self.assertNotIn("['systemctl', 'daemon-reload']",raw)
        self.assertNotIn("['systemctl', 'start'",raw)
        self.assertIn("int(st[19]) == 10125088",raw)


if __name__=='__main__':unittest.main()
