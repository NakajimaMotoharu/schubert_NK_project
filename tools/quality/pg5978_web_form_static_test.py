import unittest
from unittest.mock import patch
from pyflakes.api import check
import pg5978_web_form_static as t


class Web22StaticDefinitionTest(unittest.TestCase):
    def test_baseline_namespace_and_exact_raw_delta(self):
        self.assertEqual(t.OLD, t.plan()['source']); raw = t.runner_source()
        names = sorted(k for k in vars(t.previous.previous) if k.isidentifier() and not k.startswith('__') and k != 'main')
        self.assertEqual(0, check('='.join(names)+'=None\ndebug_proof=None\n'+raw, '<pure Web22 static namespace>'))
        self.assertIn('(921,149)', raw); self.assertIn('PG5978-web-form-static-v1', raw)
        t.expected_rules({'AvoidLiteralsInIfCondition':115,'Other':1},{'AvoidLiteralsInIfCondition':93,'Other':1})
        with self.assertRaises(ValueError):
            t.expected_rules({'AvoidLiteralsInIfCondition':115,'Other':1},{'AvoidLiteralsInIfCondition':93,'Other':0})

    def test_only_declared_web_owner_changes(self):
        old={str(i)+'.class':'a' for i in range(1666)};old['web:A.class']=old.pop('0.class');new=dict(old);new['web:A.class']='b'
        with patch.object(t, 'plan', return_value={'sourcePlans':[{'path':'src/schubert-nk-web/src/main/java/A.java'}]}):
            self.assertEqual(['web:A.class'], t.physical_changes(old,new))
            with self.assertRaises(ValueError):
                t.physical_changes(old,{**new,'1.class':'wrong'})


if __name__ == '__main__':
    unittest.main()
