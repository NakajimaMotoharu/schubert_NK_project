"""Actual corrected dispatcher input schema and closed recursive archive scope."""
import copy
import json
import unittest
import pg1387_role_dispatch_v3 as p

class Test(unittest.TestCase):
    def test_actual_full_generation_and_negative_schema(self):
        e=p.environment();w=e['W'];f=json.loads((w/'pg1385-frozen-v2.safe.json').read_bytes());g=json.loads((w/'pg1386-role-fresh-preflight-v1.safe.json').read_bytes())
        self.assertEqual(f['fileHashes'],e['qualify'](f,g))
        self.assertIn('Pg1380BootstrapRolePreparation.class',f['fileHashes'])
        self.assertIn('pg1380_bootstrap_role_refs.py',f['fileHashes'])
        for value in (False,None,'0',1):
            bad=copy.deepcopy(f);bad['actualExit']=value
            with self.assertRaises(ValueError):e['qualify'](bad,g)
        for value in (False,0,None,'true'):
            bad=copy.deepcopy(g);bad['allClientAdvisoryFlock0']=value
            with self.assertRaises(ValueError):e['qualify'](f,bad)
        for name in ('../escape','/absolute','dev/../escape','dev//extra'):
            bad=copy.deepcopy(f);bad['fileHashes'][name]='a'*64
            with self.assertRaises(ValueError):e['qualify'](bad,g)
        raw=p.text()
        self.assertIn('seen==directories|set(FILES)',e['STAGE'])
        for name in ('pg1387-stage-v1','pg1382-role-fixed-ref-handoff-v1','Pg1380BootstrapRolePreparation prepare','operatorSourceAtStart','operatorHeadAtEnd'):
            self.assertIn(name,raw)
        for name in ('pg1377-','pg1374-','Pg1374BootstrapRolePreparation','pg1368-bootstrap-fixed-ref-handoff-v1'):
            self.assertNotIn(name,raw)

if __name__=='__main__':unittest.main()
