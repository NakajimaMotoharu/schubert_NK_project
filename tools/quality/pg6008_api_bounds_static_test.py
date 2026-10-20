import unittest
from unittest.mock import patch
from pyflakes.api import check
import pg6008_api_bounds_static as t


class Api15RawStaticBindingTest(unittest.TestCase):
    def test_actual_baseline_all851_namespace_and_delta18(self):
        self.assertEqual(t.OLD,t.plan()['source']);raw=t.runner_source()
        names=sorted(k for k in vars(t.namespace_engine)if k.isidentifier()and not k.startswith('__')and k!='main')
        self.assertEqual(0,check('='.join(names)+'=None\ndebug_proof=executable_proof=None\n'+raw,'<API15 complete static namespace>'))
        self.assertIn('(1021,175)',raw);self.assertIn('all15ExecutableProof',raw)
        self.assertIn("target = BASE/'PG6008-api-bounds-static-v1'",raw)
        t.expected_rules({'AvoidLiteralsInIfCondition':51,'Other':1},{'AvoidLiteralsInIfCondition':33,'Other':1})
        with self.assertRaises(ValueError):t.expected_rules({'AvoidLiteralsInIfCondition':51,'Other':1},{'AvoidLiteralsInIfCondition':33,'Other':0})

    def test_exact_api_owner_physical_scope(self):
        old={str(i)+'.class':'a'for i in range(1666)};old['api:A.class']=old.pop('0.class');new={**old,'api:A.class':'b'}
        with patch.object(t,'plan',return_value={'sourcePlans':[{'path':'src/schubert-nk-api/src/main/java/A.java'}]}):
            self.assertEqual(['api:A.class'],t.physical_changes(old,new))
            with self.assertRaises(ValueError):t.physical_changes(old,{**new,'1.class':'bad'})


if __name__=='__main__':unittest.main()
