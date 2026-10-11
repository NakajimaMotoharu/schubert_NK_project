"""Exact actual AST-rendered peer SQL, independent literal at backend boundaries."""
import ast
import unittest
import pg1380_bootstrap_role_sources_v3 as p

class Test(unittest.TestCase):
    def test_whole_rendered_sql_matches_independent_literal(self):
        raw=p.files()['pg1380_bootstrap_role_refs.py'];tree=ast.parse(raw)
        holder=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='holder')
        query=next(n for n in holder.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='q'for t in n.targets))
        for backend in (2,42,2147483647):
            scope={'backend':backend};exec(compile(ast.Module(body=[query],type_ignores=[]),'<actual rendered peer SQL>', 'exec'),scope)
            expected="select count(*)from pg_stat_activity a where pid="+str(backend)+" and datname='schubert_nk'and usename='schubert_batch'and application_name='PG998-bootstrap-role'and client_addr=inet '127.0.0.1'and exists(select 1 from pg_locks l where l.pid=a.pid and l.locktype='advisory'and l.classid=0 and l.objid=71419602 and l.objsubid=1 and l.mode='ExclusiveLock'and l.granted);"
            self.assertEqual(expected,scope['q'])
            self.assertFalse(str(backend)+'and'in scope['q'])
        self.assertTrue('Pg1380BootstrapRolePreparation'in raw)
        self.assertFalse('Pg1374BootstrapRolePreparation'in raw)

if __name__=='__main__':unittest.main()
