import ast
import unittest
from pg1247_fresh_owned_stop_sources import sources, OWNED, BEFORE, GUEST_BEFORE

class CurrentFreshStopClosureTest(unittest.TestCase):
    def test_actual_owned_generation_function_and_all_generated_imports(self):
        files=sources();self.assertEqual(len(files),13)
        witness={};exec(compile(files['pg526_term_witness.py'],'<qualified exact terminal fields>','exec'),witness)
        tree=ast.parse(files['pg1247_native_owned_stop.py'])
        nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in {'require','validate_live'}or isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id in {'ORDER','EXPECTED'}for t in n.targets)]
        ns={'FIELDS':witness['FIELDS']};exec(compile(ast.Module(body=nodes,type_ignores=[]),'<actual new generation validation>','exec'),ns)
        captured={u:{k:''for k in ns['FIELDS']}for u in ns['ORDER']}
        for u,(pid,inv)in OWNED.items():
            captured[u].update(MainPID=pid,InvocationID=inv,ActiveState='active',SubState='running',ControlPID='0',Result='success',Id=u,LoadState='loaded',ExecMainCode='0',ExecMainStatus='0',ExecMainExitTimestampMonotonic='0')
        ns['validate_live'](captured)
        for u in OWNED:
            for key,bad in [('MainPID','0'),('InvocationID','a'*32),('ActiveState','inactive'),('Result','timeout')]:
                altered={k:dict(v)for k,v in captured.items()};altered[u][key]=bad
                with self.assertRaises(ValueError):ns['validate_live'](altered)
        refs=files['pg1247_native_refs.py']
        self.assertIn(GUEST_BEFORE,refs);self.assertIn(BEFORE,refs)
        self.assertNotIn("prior['trees']",refs)
        for name,s in files.items():
            if name.endswith('.py'):
                compile(s,'<actual complete fixed source>','exec')
                for node in ast.walk(ast.parse(s)):
                    if isinstance(node,ast.ImportFrom)and node.module and node.module.startswith(('pg1247','pg526')):
                        self.assertIn(node.module+'.py',files)
            for obsolete in ['a14cc600a4fd4f2e9d8c4731ad9d754b','343a5a1b-d064-47d5-88c2-31c36d7ba7a4','Pg1216','pg1216']:
                self.assertNotIn(obsolete,s)
        self.assertIn('PG998-native-stop',files['Pg1247NativeStop.java'])

if __name__=='__main__':unittest.main()
