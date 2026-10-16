import ast
import unittest
from pyflakes.api import check
import pg4168_retained_pair_keeper as p


class KeeperTest(unittest.TestCase):
    def test_complete_closure_two_fixed_targets_and_no_business_or_force_operation(self):
        raw=p.payload();self.assertEqual(0,check(raw,'<keeper>'))
        tree=ast.parse(raw)
        calls=[n for n in ast.walk(tree)if isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id=='terminate']
        self.assertEqual([(790010,14181503),(789928,14180650)],[(c.args[0].value,c.args[1].value)for c in calls])
        self.assertTrue(raw.index("frame('SSC288_PAIR_READY '")<raw.index('  terminate(790010'))
        self.assertFalse("'systemctl','stop'"in raw or "'/usr/bin/systemctl','stop'"in raw)
        self.assertFalse('signal.SIGKILL'in raw or 'pg_terminate_backend'in raw)
        self.assertTrue("frame('SSC288_METADATA_HELD postRequired=true',1800)"in raw)
        self.assertTrue("while True:time.sleep(1)"in raw)

    def subject(self,exists=True,state='Z',ticks=14181503,parent=789928,files=()):
        class Fake:
            def __truediv__(self,unused):return self
            def exists(self):return exists
            def read_text(self):
                fields=[state,str(parent),*['0']*17,str(ticks),*['0']*20]
                return '790010 (java) '+' '.join(fields)
            def iterdir(self):return iter(files)
        node=next(n for n in ast.parse(p.payload()).body if isinstance(n,ast.FunctionDef)and n.name=='zombie_or_absent')
        ns={'Path':lambda unused:Fake()};exec(compile(ast.Module(body=[node],type_ignores=[]),'<actual terminal predicate>','exec'),ns)
        return ns['zombie_or_absent'](790010,14181503,789928)

    def test_only_exited_same_generation_child_no_live_recycled_or_fd_owner(self):
        self.assertTrue(self.subject(exists=False))
        self.assertTrue(self.subject())
        for change in [{'state':'S'},{'ticks':1},{'parent':1},{'files':['fd']}]:
            with self.subTest(change=change):self.assertFalse(self.subject(**change))


if __name__=='__main__':unittest.main()
