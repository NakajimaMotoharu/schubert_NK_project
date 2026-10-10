import ast
import unittest
import pg1228_completed_runtime_dispatch as p

class DispatchTest(unittest.TestCase):
    def test_actual_namespace_and_exact_stage_closure(self):
        s=p.source();env={'__name__':'qualified_runtime_dispatch','__file__':p.__file__}
        exec(compile(s,'<actual retirement dispatch namespace>','exec'),env)
        env['bindings'](env['proof']());self.assertEqual(env['GUEST'],'/var/lib/pgpt-s1-preservation/pg1224-native-tools-v2')
        compile(env['STAGE'],'<actual archive stage>','exec')
        oracle=env['archive_members'];oracle([('pkg','dir'),('pkg/a','file')],{'pkg/a'})
        for bad in [[('../a','file')],[('/a','file')],[('a','file'),('a','file')],[('a','symlink')]]:
            with self.assertRaises(ValueError):oracle(bad,{'a'})
        for part in ["(['stage'],['retire'])","'Pg1224NativeStop retire'","pre['actualDisjointScopeOracle']","frozen['completedBeforeSha256']",'pg1226-frozen-v1.safe.json']:
            self.assertTrue(part in s,part)
        self.assertFalse('Pg1224NativeStop stop'in s)
        for n,v in env['generate'](None).items():
            if n.endswith('.py'):compile(v,'<actual v2 '+n+'>','exec')

if __name__=='__main__':unittest.main()
