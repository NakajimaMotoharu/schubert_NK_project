import ast
import unittest
from pg1164_runtime_failed_owner_proof import payload


class RuntimeOwnerTest(unittest.TestCase):
    def test_fixed_wrong_runtime_owner_and_allfield_policy(self):
        s=payload();t=ast.parse(s)
        for p in ['JAVA=415524;CHILD=415553','4807423','4807540','reload_policy.configuration(','d344cecf96e7a5219adf22b312420ff6e0a1b314834d230e476c507ade7903b0','runtime-failed-owner-proof-v1','pg1160-runtime-tools-v1']:
            self.assertTrue(p in s,p)
        self.assertFalse('pidfd_send_signal'in s);self.assertFalse('systemctl start'in s)
        n=[n for n in t.body if isinstance(n,ast.Assign)and any(isinstance(k,ast.Name)and k.id=='NATIVE_FILES'for k in n.targets)]
        self.assertEqual(len(n),1);self.assertIn('pg1160_runtime_refs.py',ast.literal_eval(n[0].value))


if __name__=='__main__':unittest.main()
