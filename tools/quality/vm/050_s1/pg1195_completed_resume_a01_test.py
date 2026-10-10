import ast
import unittest
from pg1195_completed_resume_a01 import code, guard, qualify_actor


class CompletedA01Test(unittest.TestCase):
    def test_independent_ordinary_identity_caps_and_entry_negatives(self):
        unit='schubert-nk-api.service';status={'Uid':'999 999 999 999','Gid':'981 981 981 981','Groups':'980 981 982 986','NoNewPrivs':'1',**{k:'0000000000000000'for k in ['CapInh','CapPrm','CapEff','CapBnd','CapAmb']}}
        exe='/opt/jdk-25.0.4/bin/java';argv=b'/opt/jdk-25.0.4/bin/java\0dev.codex.schubert.nk.api.bootstrap.ApiProcessMain\0'
        qualify_actor(unit,status,exe,argv)
        for key in status:
            for value in [None,'foreign']:
                with self.assertRaises(ValueError):qualify_actor(unit,dict(status,**{key:value}),exe,argv)
        for bad in [None,{},dict(status,extra='raw')]:
            with self.assertRaises(ValueError):qualify_actor(unit,bad,exe,argv)
        for bad in [None,b'',b'foreign']:
            with self.assertRaises(ValueError):qualify_actor(unit,status,exe,bad)
        with self.assertRaises(ValueError):qualify_actor(unit,status,'/usr/bin/foreign',argv)
    def test_actual_new_receipt_and_same_generations_without_root_extension(self):
        s=code();g=guard();ast.parse(s);ast.parse(g)
        for part in ['result=qualify(BINDING,rows,done)','project(again)!=project(raw)','currentStateClass=qualify_current(state)','52530445203','bfae0cf915c74f7bbf35a7a1ec4f8cd9','898429f0e6a64d4fa7a6c07e4473fe8a','1037150931c04cb6b64b249c0cf916c3','5227058','5228431','5230806']:
            self.assertTrue(part in g,part)
        self.assertFalse('private.mkdir(' in g)
        self.assertFalse('time.monotonic_ns()//1000' in g)
        self.assertTrue('1800000000' in g or '1_800_000_000' in g)
        self.assertTrue('pg1195-chr-a01-native-v1' in s)
        self.assertEqual(s.count('require_owner()'),3)
        self.assertFalse('pg1192-chr-a01-native-v1' in s)
        for forbidden in ['systemctl start','systemctl stop','daemon-reload']:
            self.assertFalse(forbidden in g,forbidden)


if __name__=='__main__':unittest.main()
