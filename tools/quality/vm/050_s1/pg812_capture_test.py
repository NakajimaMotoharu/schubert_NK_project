"""Capture-only row comparison; literal nested JSON/multiset/phase oracle, no VM."""
import ast
import collections
import json
import unittest
from pg812_current_capture import PAYLOAD

class CaptureTest(unittest.TestCase):
    def test_nested_json_and_duplicate_changes(self):
        node=next(n for n in ast.parse(PAYLOAD).body if isinstance(n,ast.FunctionDef)and n.name=='row_delta')
        env={'collections':collections,'json':json};exec(compile(ast.Module(body=[node],type_ignores=[]),'<capture delta>','exec'),env)
        before={str(i):[]for i in range(24)};after={str(i):[]for i in range(24)}
        before['0']=[{'id':1,'value':{'a':[None,2]}},{'id':1,'value':{'a':[None,2]}}]
        after['0']=[{'value':{'a':[None,2]},'id':1},{'id':2,'value':{'a':[None,3]}},{'id':3}]
        self.assertEqual(env['row_delta'](before,after),{'0':{'beforeCount':2,'actualCount':3,'removedCount':1,'addedCount':2}})
        self.assertEqual(env['row_delta'](before,before),{})
        with self.assertRaises(AssertionError):env['row_delta'](before,{})

    def test_capture_not_old_acceptance(self):
        ast.parse(PAYLOAD)
        self.assertIn("current_rows=namespace['rows']",PAYLOAD)
        self.assertIn('row_delta(old[',PAYLOAD)
        self.assertIn('rowChangesNotAccepted',PAYLOAD)
        self.assertNotIn('h.rows()',PAYLOAD)
        self.assertNotIn('systemctl\',\'stop',PAYLOAD)

if __name__=='__main__':unittest.main()
