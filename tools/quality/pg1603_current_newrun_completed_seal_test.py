"""Independent literal binding, exact SQL oracle, ownership and scope lifetime."""
import ast
import unittest
from pg1603_current_newrun_completed_seal import payload,once
from pg1602_current_newrun_rows_oracle_test import NewRunSqlOracleTest

class FullCurrentSealTest(unittest.TestCase):
    def test_actual_source_binding_and_independent_sql(self):
        raw=payload();tree=ast.parse(raw)
        literals={}
        for n in tree.body:
            if isinstance(n,ast.Assign)and len(n.targets)==1 and isinstance(n.targets[0],ast.Name)and n.targets[0].id in {'ORACLE','GUARD','OWNED'}:
                literals[n.targets[0].id]=ast.literal_eval(n.value)
        self.assertEqual(set(literals['OWNED']),{'artemis.service','schubert-nk-api.service','schubert-nk-web.service','caddy.service'})
        self.assertEqual(literals['OWNED']['schubert-nk-api.service'][:3],('256734','994fd53232ee426d9ca93a2f311bda53',3946268))
        self.assertEqual(literals['OWNED']['schubert-nk-web.service'][:3],('257744','7a75a61efae5403692eb523eea322c19',3947570))
        self.assertIn('e4d891c38dde4e16a5c848e23ef3f83c',literals['GUARD'])
        self.assertIn('38365395523',literals['GUARD'])
        for old in ['c52c914a72804a89b0fd5f252f6ac0fc','15700a87-9117-4f63-a0ff-768dd604d0f1','33583425972','1539.994702']:
            self.assertNotIn(old,raw)
        self.assertIn('pg1596-current-ordinary-before-v1/before.private.json',raw)
        self.assertIn("proof.done.decode('ascii').splitlines()[4]",raw)
        self.assertNotIn("proof.result['endInstant']",raw)
        env={};exec(compile(literals['ORACLE'],'<independent literal SQL fixture>','exec'),env)
        old,new=NewRunSqlOracleTest().fixture()
        self.assertEqual(env['qualify'](old,new,'2026-10-12T06:23:13.176261Z','2026-10-12T06:45:00Z')['newSkippedSteps'],10)
        new['schubert.batch_runs'][-1]['attempt']=1
        with self.assertRaises(ValueError):env['qualify'](old,new,'2026-10-12T06:23:13.176261Z','2026-10-12T06:45:00Z')
        life=next(n for n in tree.body if isinstance(n,ast.Try))
        self.assertGreaterEqual(sum(isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id=='capture'for n in ast.walk(life)),3)
        self.assertIn('UnrefUnit',ast.unparse(ast.Module(body=life.finalbody,type_ignores=[])))
        self.assertNotIn('StartUnit',raw);self.assertNotIn('StopUnit',raw)
        for old,new in [('absent','unused'),('x','y')]:
            with self.assertRaises(ValueError):once('xx',old,new)

if __name__=='__main__':unittest.main()
