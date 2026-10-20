import unittest
from unittest.mock import patch
from pyflakes.api import check
import pg5992_web_contract_static as t


class Current24RawStaticDefinitionTest(unittest.TestCase):
    def test_all851_namespace_and_actual_source_baseline(self):
        self.assertEqual(t.OLD,t.plan()['source']); raw=t.runner_source()
        names=sorted(k for k in vars(t.previous.previous.previous) if k.isidentifier() and not k.startswith('__') and k!='main')
        self.assertEqual(0,check('='.join(names)+'=None\ndebug_proof=None\n'+raw,'<Web24 complete static namespace>'))
        self.assertIn("'pg5978-web-form-static-v1/manifest.safe.json'",raw)
        self.assertIn("target = BASE/'PG5992-web-contract-static-v1'",raw)
        t.expected_rules({'AvoidLiteralsInIfCondition':93,'Other':1},{'AvoidLiteralsInIfCondition':51,'Other':1})
        with self.assertRaises(ValueError):
            t.expected_rules({'AvoidLiteralsInIfCondition':93,'Other':1},{'AvoidLiteralsInIfCondition':51,'Other':0})

    def test_physical_change_guard_rejects_unrelated_owner(self):
        old={str(i)+'.class':'a' for i in range(1666)};old['web:A.class']=old.pop('0.class');new={**old,'web:A.class':'b'}
        with patch.object(t,'plan',return_value={'sourcePlans':[{'path':'src/schubert-nk-web/src/main/java/A.java'}]}):
            self.assertEqual(['web:A.class'],t.physical_changes(old,new))
            with self.assertRaises(ValueError):
                t.physical_changes(old,{**new,'1.class':'bad'})


if __name__ == '__main__':
    unittest.main()
