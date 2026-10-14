"""New fullseal old-preimage refusal, authority single bindings and independent day15 graph."""
import ast
import unittest
from pyflakes.api import check
import pg2886_network_newcurrent_full_seal as p


class FullSeal(unittest.TestCase):
    def test_current_admission_real_shape_and_no_after_as_before(self):
        b={'boot':'79a3260ae16d42bf942ab914ed144c28','invocation':'d4197711cfc54770a4ac7c8d90a3a576','job':'11471','start':4396782047,
            'run':'0dc63b79-3f9a-450c-b2a6-56f86272d272','cutoff':'2026-10-14T19:12:28.842213Z','activation':'74729e17-91c0-43e7-b01f-74f9e6461d6a','rootPid':27414}
        raw=p.payload(b);self.assertEqual(0,check(raw,'<whole current seal>'))
        for v in ['external-before.private.json','22cb3a9aa8589859ecdab540cb31ea8e0c06cc07f7ebb7ab171bef4aa3e26b80',p.SOURCE,p.BOM,
            "before={'configuration':immutable['configuration'],'rows':immutable['rows'],'durable':immutable['durable']}",
            "not os.listdir(root)",'runtime=isolation_runtime()']:
            self.assertTrue(v in raw,v)
        self.assertFalse("before['oneTimeRuntime']"in raw)
        self.assertFalse('pg2684-operation-current-noargs-once-v2/before.private.json'in raw)
        self.assertFalse('b2d6f605' in raw)
        t=ast.parse(raw)
        for key in ['GUARD','ORACLE','BOOT','SOURCE','BOM','BEFORE_HASH']:
            self.assertEqual(1,sum(isinstance(n,ast.Assign)and any(isinstance(q,ast.Name)and q.id==key for q in n.targets)for n in t.body),key)
        o=p.oracle(b);self.assertEqual(0,check(o,'<actual day15 independent SQL>'))
        self.assertTrue("r['business_date']=='2026-10-15'"in o)


if __name__=='__main__':unittest.main()
