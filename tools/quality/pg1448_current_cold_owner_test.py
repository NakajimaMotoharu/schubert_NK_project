"""Independent golden metadata/link semantics and no-authority build checks."""
import ast
import types
import unittest
from pg1448_current_cold_owner import BODY,payload


class OwnerProofTest(unittest.TestCase):
    def test_nine_fields_and_link_following(self):
        node=next(n for n in ast.parse(BODY).body if isinstance(n,ast.FunctionDef)and n.name=='meta_any')
        ns={};exec(compile(ast.Module(body=[node],type_ignores=[]),'<metadata oracle>','exec'),ns)
        actual=types.SimpleNamespace(**dict(zip(['st_dev','st_ino','st_uid','st_gid','st_mode','st_nlink','st_size','st_mtime_ns','st_ctime_ns'],[28,1997,0,0,33152,1,0,701,702])))
        link=types.SimpleNamespace(**dict(zip(['st_dev','st_ino','st_uid','st_gid','st_mode','st_nlink','st_size','st_mtime_ns','st_ctime_ns'],[5,8,0,0,41471,1,37,901,902])))
        path=types.SimpleNamespace(stat=lambda:actual,lstat=lambda:link)
        self.assertEqual([28,1997,0,0,33152,1,0,701,702],ns['meta_any'](path,True))
        self.assertEqual([5,8,0,0,41471,1,37,901,902],ns['meta_any'](path,False))

    def test_fixed_modes_and_namespace_initialization(self):
        for mode in ['observe','handoff']:
            source=payload(mode);compile(source,'<fixed payload>','exec')
            tree=ast.parse(source);names=[]
            for n in tree.body:
                if isinstance(n,ast.Expr)and isinstance(n.value,ast.Call)and isinstance(n.value.func,ast.Name)and n.value.func.id=='exec'and len(n.value.args)==2 and isinstance(n.value.args[1],ast.Name):
                    names.append(n.value.args[1].id)
            self.assertEqual(['CAPTURE_BOUND','CONFIG_CONTRACT','UNIT_VECTOR'],sorted(n for n in names if n in {'UNIT_VECTOR','CAPTURE_BOUND','CONFIG_CONTRACT'}))
            self.assertIn("PID=3323;TICKS=388541;BACKEND=3344",source)
            self.assertIn("contract.terminate_once",source)
            attributes=[n.attr for n in ast.walk(tree)if isinstance(n,ast.Attribute)]
            self.assertNotIn('SIGKILL',attributes)
            calls=[ast.unparse(n.func)for n in ast.walk(tree)if isinstance(n,ast.Call)]
            self.assertNotIn('os.kill',calls)
        for mode in [None,'', 'prepare', 'replay']:
            with self.assertRaises(ValueError):payload(mode)


if __name__=='__main__':unittest.main()
