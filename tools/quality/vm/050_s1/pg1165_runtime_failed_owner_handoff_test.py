import ast
import unittest
from pg1165_runtime_failed_owner_handoff import source


class RuntimeHandoffTest(unittest.TestCase):
    def test_exact_owner_original_runtime_current_closure(self):
        raw=source();self.assertTrue('pg1165-runtime-failed-owner-handoff-v1'in raw)
        self.assertFalse('pg1157-runtime-failed-owner-handoff-v1'in raw)
        ns={'__name__':'data','__file__':__file__};exec(raw,ns);s=ns['payload']();t=ast.parse(s)
        for p in ['terminate_once(415553,4807540','terminate_once(415524,4807423','runtime-failed-owner-handoff-v1','8f0794b3466ea22bbff455b907788ed7976a3c4869b2ed7b7452a84acdc971d5','d344cecf96e7a5219adf22b312420ff6e0a1b314834d230e476c507ade7903b0']:
            self.assertTrue(p in s,p)
        self.assertEqual(len([n for n in t.body if isinstance(n,ast.FunctionDef)and n.name=='current']),1)
        self.assertLess(s.index('terminate_once(415553'),s.index('terminate_once(415524'))
        self.assertFalse('systemctl stop'in s);self.assertFalse('systemctl start'in s)


if __name__=='__main__':unittest.main()
