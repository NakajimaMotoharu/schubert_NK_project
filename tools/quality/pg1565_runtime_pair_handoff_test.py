"""Actual composed finite ownership handoff; no VM action in this test."""
import ast
import unittest
from pg1565_runtime_pair_handoff import payload as handoff
from pg1566_runtime_pair_closing import payload as closing

class HandoffTest(unittest.TestCase):
    def test_exact_current_signal_and_reap_no_business_or_replay(self):
        s=handoff();tree=ast.parse(s)
        calls=[n for n in ast.walk(tree)if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and n.func.attr=='terminate_once']
        self.assertEqual(len(calls),2);self.assertEqual([n.args[0].value for n in calls],[105232,105206])
        self.assertIn('wait_reaped(105232,CHILD_TICKS)',s);self.assertIn('wait_reaped(105206,3041121)',s)
        self.assertIn('PG271-runtime-once',s);self.assertNotIn('PG269-original-io-profile',s)
        for banned in ['daemon-reload','StartUnit','StopUnit','runtime.owned_prepare(']:self.assertNotIn(banned,s)
        t=ast.parse(closing());calls=[n for n in ast.walk(t)if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and n.func.attr=='terminate_once']
        self.assertEqual(calls,[])
        text=closing();self.assertIn("'105206.term-once.private'",text);self.assertIn("'105232.term-once.private'",text)
        self.assertIn('validate_current(first)',text);self.assertIn('oldNormalCloseUnknown',text)

if __name__=='__main__':unittest.main()
