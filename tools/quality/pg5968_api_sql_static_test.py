import unittest
from unittest.mock import patch
from pyflakes.api import check
import pg5968_api_sql_static as t


class Sql21IndependentStaticDefinitionTest(unittest.TestCase):
    def test_complete_namespace_and_exact_raw_count_guard(self):
        self.assertEqual(t.plan()['source'], t.OLD)
        raw = t.runner_source(); names = sorted(k for k in vars(t.previous) if k.isidentifier() and not k.startswith('__') and k != 'main')
        self.assertEqual(0, check('='.join(names)+'=None\ndebug_proof=None\n'+raw, '<pure SQL21 static definition>'))
        self.assertIn('1021,175', raw); self.assertIn('PG5968-api-sql-static-v1', raw)
        t.expected_rules({'AvoidLiteralsInIfCondition': 136, 'Other': 10}, {'AvoidLiteralsInIfCondition': 115, 'Other': 10})
        with self.assertRaises(ValueError):
            t.expected_rules({'AvoidLiteralsInIfCondition': 136, 'Other': 10}, {'AvoidLiteralsInIfCondition': 115, 'Other': 9})

    def test_no_missing_target_foreign_owner_or_added_class(self):
        old = {str(i)+'.class':'before' for i in range(1666)};old['api:A.class']=old.pop('0.class'); new=dict(old);new['api:A.class']='after'
        with patch.object(t, 'plan', return_value={'sourcePlans':[{'path':'src/schubert-nk-api/src/main/java/A.java'}]}):
            self.assertEqual(['api:A.class'], t.physical_changes(old, new))
            for bad in (old, {**new,'1.class':'wrong'}, {**new,'extra.class':'new'}):
                with self.assertRaises(ValueError):
                    t.physical_changes(old, bad)


if __name__ == '__main__':
    unittest.main()
