import ast
import unittest
import pg1224_completed_runtime_sources as p

class GeneratedRetirementTest(unittest.TestCase):
    def test_actual_namespaces_protocol_and_terminal_fixed_baseline(self):
        values=p.generated();refs=values['pg1224_native_refs.py'];tree=ast.parse(refs)
        self.assertTrue(p.BASE in refs);self.assertTrue(p.SHA in refs)
        for old in ['full32-stop-owner-handoff-v1/after.private.json','h.stop_one(',"action.startswith('stop:')","require(prior['source']"]:
            self.assertFalse(old in refs,old)
        for required in ['retirement.retire_entry(',"['before','retire','terminal','release']",'prior.items()',"'native':tree(","h.kernel_empty(u)","capture_data(False)"]:
            self.assertTrue(required in refs,required)
        # Import-like whole helper namespace: main is defined, never dispatched.
        for n,s in values.items():
            if n.endswith('.py'):
                compile(s,'<actual generated '+n+'>','exec')
        main=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='main')
        self.assertGreater(main.end_lineno-main.lineno,80)
        j=values['Pg1224NativeStop.java']
        self.assertTrue('refs.check("retire")'in j)
        self.assertTrue('"retire".equals(name)'in j)
        self.assertFalse('for(var unit:'in j)
        self.assertFalse('name.startsWith("stop:")'in j)
        self.assertTrue('db.rollback();db.close();lease.confirmClosed()'in j)
        self.assertTrue('new String[]{"stop"}'in values['Pg1224NativeArgumentTest.java'])
        self.assertFalse('new String[]{"retire"}'in values['Pg1224NativeArgumentTest.java'])

if __name__=='__main__':unittest.main()
