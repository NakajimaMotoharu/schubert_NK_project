"""Fixed once generation and complete former scope/data post; no start authority."""
import ast
import unittest
from pg1114_readonly_nested_retirement import payload


class NestedRetirement(unittest.TestCase):
    def test_exact_once_target_and_scope(self):
        s=payload();tree=ast.parse(s)
        calls=[n for n in ast.walk(tree)if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and n.func.attr=='terminate_once']
        self.assertEqual(1,len(calls));self.assertEqual([134103,3382984],[ast.literal_eval(a)for a in calls[0].args[:2]])
        attrs={n.attr for n in ast.walk(tree)if isinstance(n,ast.Attribute)}
        self.assertNotIn('StartUnit',attrs);self.assertNotIn('SIGKILL',attrs)
        self.assertIn('SIGTERM',attrs);self.assertIn('durable_reservation',attrs)
        self.assertTrue('pg1106-ordinary-cold-before-v1/nested-once-v1'in s)
        self.assertTrue("assert after==before['post']==post()"in s)
        self.assertTrue('OLD_BUS'in s)


if __name__=='__main__':unittest.main()
