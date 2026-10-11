import ast
import unittest
from pg1453_current_cold_post import payload


class PostOracleTest(unittest.TestCase):
    def test_fixed_expected_role_matrix(self):
        tree=ast.parse(payload())
        n=next(n for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='ROLE_IDS'for t in n.targets))
        self.assertEqual({'backup':(992,977),'cleanup':(0,0),'expiry':(0,0),'inspector':(991,976),'ordinary-api193':(999,981),'ordinary-bootstrap196':(999,981),'ordinary-inspector196':(991,976),'ordinary-web193':(997,980),'parent':(0,0),'root-api':(0,0),'root-api193':(0,0),'root-web193':(0,0)},ast.literal_eval(n.value))

    def test_no_authority_or_original_rewrite(self):
        s=payload();compile(s,'<independent post>','exec')
        calls=[ast.unparse(n.func)for n in ast.walk(ast.parse(s))if isinstance(n,ast.Call)]
        for denied in ['os.kill','signal.pidfd_send_signal','manager.StartUnit','manager.StopUnit','os.chmod','os.chown']:self.assertNotIn(denied,calls)
        self.assertIn("[b'0',b'0']",s)
        self.assertIn("'ro'in opts and 'rw'not in opts",s)
        self.assertIn("stat.S_IFDIR|0o755,14",s)
        self.assertIn("metadata(ROOT)[2:6]==[0,0,stat.S_IFDIR|0o755,8]",s)


if __name__=='__main__':unittest.main()
