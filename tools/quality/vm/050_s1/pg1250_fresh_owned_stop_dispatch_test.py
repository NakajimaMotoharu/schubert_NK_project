import ast
import unittest
from pg1250_fresh_owned_stop_dispatch import STAGE

class FreshImmutableStageTest(unittest.TestCase):
    def test_actual_archive_closure_and_fixed_new_slots(self):
        ns={}
        tree=ast.parse(STAGE)
        fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='archive_members')
        exec(compile(ast.Module(body=[fn],type_ignores=[]),'<actual strict archive closure>','exec'),ns)
        ns['archive_members']([('a.py','file'),('dir','dir'),('dir/b.class','file')],{'a.py','dir/b.class'})
        for bad in [[('../a.py','file')],[('a.py','file'),('a.py','file')],[('a.py','link')],[('a.py','file')],[('foreign','dir'),('a.py','file'),('dir','dir'),('dir/b.class','file')]]:
            with self.assertRaises(ValueError):ns['archive_members'](bad,{'a.py','dir/b.class'})
        self.assertIn('/home/ubuntu/pg1250-fixed-stage-v1/pg1247-native-tools-v1.tar',STAGE)
        self.assertIn('/var/lib/pgpt-s1-preservation/pg1247-native-tools-v1',STAGE)
        self.assertNotIn('pg1198',STAGE);self.assertNotIn('pg1201',STAGE)
        compile(STAGE,'<actual whole immutable stage>','exec')

if __name__=='__main__':unittest.main()
