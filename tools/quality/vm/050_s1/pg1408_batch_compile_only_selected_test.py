"""Independent phase literal and unknown/full lifecycle refusal; no quality waiver."""
import unittest
import pg1408_batch_compile_only_selected_v3 as p

class Test(unittest.TestCase):
    def test_exact_goals_and_bad_lifecycle(self):
        gold=['spotless:check','compile','jar:jar','install:install']
        self.assertEqual(gold,p.dependency_goals(gold))
        for bad in (None,[],['install'],['verify'],['package'],gold+['verify'],['spotless:check','compile','jar:jar','install']):
            with self.assertRaises(ValueError):p.dependency_goals(bad)
    def test_actual_scope_and_fresh_target(self):
        raw=p.source()
        self.assertIn('dependency_goals(GOALS)',raw)
        self.assertIn('len(dependency_same)==3',raw)
        self.assertIn('fresh_xml(p,suite',raw)
        self.assertIn('dependencyCompileOnlyNoPtCredit',raw)
        self.assertNotIn("'-DskipTests'",raw)
        self.assertNotIn("'spotless:check','install'",raw)
        compile(raw,'<actual corrected compile-only scope>','exec')

if __name__=='__main__':unittest.main()
