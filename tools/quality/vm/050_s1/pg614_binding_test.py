"""New8 current source, fixed full hashes and preserved window policy. No VM actions."""
import ast
from pathlib import Path
import unittest
R=Path(__file__).resolve().parent


class Test(unittest.TestCase):
    def test_only_current_eight_and_fresh_host_source(self):
        s=(R/'pg614_native_counter.py').read_text();t=ast.parse(s)
        values={x.id:ast.literal_eval(n.value)for n in t.body if isinstance(n,ast.Assign)for x in n.targets
                if isinstance(x,ast.Name)and x.id in ('SOURCE','HASHES','PAYLOAD')}
        self.assertEqual(values['SOURCE'],'23b14a44b10504172e030bbd6625926bf049fb5c')
        self.assertEqual(len(values['HASHES']),8)
        self.assertEqual(values['HASHES']['parent/parent.exec'],'42f52d94aab7572ef81f1eb2fb1c65b1c8f3859e3ab95db5d32110a72c32c928')
        p=values['PAYLOAD'];ast.parse(p)
        self.assertIn("start=86264628081;end=87761979588",p)
        self.assertIn("'JOB_ID')=='87863'",p)
        self.assertIn("'INVOCATION_ID']=='5a1acaa0c35e484c979401e3b6dfb36a'",p)
        self.assertIn("assert len(selected)==8",p)
        self.assertIn('metadata(s)==metadata(p.lstat())',p)
        self.assertIn("NativeSessions571",s);self.assertIn("len(info)==1",s)
        self.assertIn('pg599-candidate-bootstrap-six-host-v1',s)
        self.assertIn('cdd971634fe0f5acabe091db476f25838a55730172d3cc07244180e708f4e47d',s)
        self.assertIn("['execSha256']",s);self.assertIn("['jarSha256']",s)
        self.assertNotIn('pg540-six-host',s);self.assertNotIn('native.append(prior',s)
        self.assertIn("historicalNativeNotImported':True",s)
        self.assertIn("classByteMismatch']==0",s)


if __name__=='__main__':unittest.main()
