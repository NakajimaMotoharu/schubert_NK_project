"""Actual baseline/SQL port argument bounds, using qualified strict metadata contract."""
import ast
import stat
import unittest
from pathlib import Path
import pg1362_current_bootstrap_sources as p
import pg1363_current_bootstrap_compile as c

class Test(unittest.TestCase):
    def test_generated_exact_bounds_and_fixed_identity(self):
        values=p.files('b'*64);raw=values['pg1362_bootstrap_existing.py'];tree=ast.parse(raw)
        calls=[n for n in ast.walk(tree)if isinstance(n,ast.Call)]
        reads=[n for n in calls if isinstance(n.func,ast.Name)and n.func.id=='strict'and n.args and isinstance(n.args[0],ast.Name)and n.args[0].id=='baseline_path']
        self.assertEqual(1,len(reads));self.assertEqual([384,67108864],[n.value for n in reads[0].args[1:]])
        sql=[n for n in calls if isinstance(n.func,ast.Name)and n.func.id=='command'and 'query + 'in ast.unparse(n)]
        self.assertEqual(1,len(sql));self.assertEqual(67108864,sql[0].args[1].value)
        self.assertTrue('PG998-bootstrap-guard'in values['Pg1362BootstrapExisting.java'])
        self.assertTrue('==634'in raw and 'hashlib.sha256(base)'in raw)
        self.assertTrue('pg1361-bootstrap-fixed-pair-handoff-v1.exit'in c.source())

    def test_actual_strict_boundary_and_security(self):
        source=Path(__file__).with_name('pg480_backup_refs.py').read_text();tree=ast.parse(source)
        node=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='strict')
        class PathPort:
            def read_bytes(self):return b'bounded fixture'
        port=PathPort()
        def require(value):
            if not value:raise ValueError('fixture refused')
        class OsPort:
            @staticmethod
            def listxattr(ignored):return []
        scope={'metadata':lambda ignored:metadata,'require':require,'stat':stat,'os':OsPort}
        exec(compile(ast.Module(body=[node],type_ignores=[]),'<actual fixed strict port>','exec'),scope)
        for size in (0,33554433,67108863,67108864):
            metadata=[28,999,0,0,stat.S_IFREG|0o600,1,size,1,1]
            self.assertEqual(b'bounded fixture',scope['strict'](port,0o600,67108864))
        for size in (-1,67108865):
            metadata=[28,999,0,0,stat.S_IFREG|0o600,1,size,1,1]
            with self.assertRaises(ValueError):scope['strict'](port,0o600,67108864)
        metadata=[28,999,1,0,stat.S_IFREG|0o600,1,33554433,1,1]
        with self.assertRaises(ValueError):scope['strict'](port,0o600,67108864)

if __name__=='__main__':
    unittest.main()
