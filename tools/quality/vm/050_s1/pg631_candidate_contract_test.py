"""Independent literal one changed factory class, no missing/added/other delta."""
import copy
import unittest
from pg631_candidate_contract import verify_delta


class DeltaTest(unittest.TestCase):
    def test_normal_and_all_module_class_unknowns(self):
        old={m:{'literal/Main.class':'a'*64}for m in ['protocol','storage','bootstrap','api','web','batch']}
        old['batch']['dev/codex/schubert/nk/batch/file/MorningBackupRetention.class']='b'*64
        new=copy.deepcopy(old);new['batch']['dev/codex/schubert/nk/batch/file/MorningBackupRetention.class']='c'*64
        self.assertEqual(verify_delta(old,new),7)
        for module in old:
            for mode in ['added','removed','changed','null','bad_digest','empty']:
                bad=copy.deepcopy(new)
                if mode=='added':bad[module]['foreign.class']='d'*64
                if mode=='removed':del bad[module]['literal/Main.class']
                if mode=='changed':bad[module]['literal/Main.class']='d'*64
                if mode=='null':bad[module]=None
                if mode=='bad_digest':bad[module]['literal/Main.class']='X'*64
                if mode=='empty':bad[module]={}
                with self.subTest(module=module,mode=mode),self.assertRaises(ValueError):verify_delta(old,bad)
        for bad in [None,{},[],{**new,'foreign':{}},old]:
            with self.assertRaises(ValueError):verify_delta(old,bad)

    def test_builder_bound_prior_current_not_candidate_and_fresh_gate(self):
        from pathlib import Path
        text=(Path(__file__).parent/'pg631_candidate_build.py').read_text()
        for literal in ["SOURCE = '36fe7a0b938489d61d17d49c1c30a6fbbef699d5'","OLD_SOURCE = '72fb7440697ee1048a5c0145055dc1cc3c577914'","OLD = W / 'pg621-release-v1'","NEXT = W / 'pg631-release-v1'","FROZEN = W / 'pg630-retention-factory-six-host-v1'",'4a2c35463b37956632b6586dfe18f07320777ea863696b25c1e14e913dd3fa1e',"gate['tests'] == 3468 and gate['suites'] == 512","assert changed <= allowed and {'VERSION', 'operations/batch.jar'} <= changed","'addedAbstractInterfaces': 0, 'addedInternalClasses': 0"]:self.assertIn(literal,text)
        compile(text,'<unexecuted candidate draft>','exec')
        self.assertLess(text.index('verify_delta(old_classes, new_classes)'),text.index('shutil.copytree(OLD, NEXT)'))
        self.assertLess(text.index("assert gate['knownOracleHold']"),text.index("'-sign'"))


if __name__=='__main__':unittest.main()
