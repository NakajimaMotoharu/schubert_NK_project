import unittest
from pg5804_rollback_static import MODIFIED,ADDED,class_key,class_contract,runner_source


class ActualRollbackDeltaTest(unittest.TestCase):
    def test_exact_addition_changes_and_no_hidden_delta(self):
        prior={str(i):'a'*64 for i in range(1656)}|{class_key(p):'a'*64 for p in MODIFIED}
        current={**prior,**{class_key(p):'b'*64 for p in MODIFIED},class_key(ADDED):'c'*64}
        self.assertEqual(9,len(class_contract(prior,current)))
        for bad in({**current,'0':'d'*64},{k:v for k,v in current.items()if k!='0'}):
            with self.assertRaises(ValueError):class_contract(prior,bad)
        raw=runner_source()
        self.assertIn("'inputSourceFiles':850",raw)
        self.assertIn("'actualAuxClasses':1665",raw)
        self.assertNotIn('guard_coverage(snapshot)',raw)
        self.assertNotIn("Counter(r['rule']for r in rows)==expected_counts",raw)

    def test_generated_body_has_complete_declared_namespace(self):
        from pyflakes.api import check
        prefix='from pg5776_jms_primary_static import W,json,ROOT,sha,os,SLOT,compile_only_artifacts,Path,TC,MODULES,subprocess,ET,diagnostic_row,Counter\nfrom pg5804_rollback_static import pg_contract,MODIFIED,ADDED\n'
        self.assertEqual(0,check(prefix+runner_source(),'<generated all850 static with actual namespace>'))


if __name__=='__main__':unittest.main()
