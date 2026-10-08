"""Current source/whole table/predicate binding; no actual data or VM action."""
import ast
from pathlib import Path
import unittest

R=Path(__file__).resolve().parent;RAW=(R/'pg553_newrun_preflight.py').read_text()
N=next(n for n in ast.parse(RAW).body if isinstance(n,ast.FunctionDef)and n.name=='accepted')
ENV={};exec(compile(ast.Module(body=[N],type_ignores=[]),'<literal output oracle>','exec'),ENV)


class Test(unittest.TestCase):
    def test_output_boundary_null_type(self):
        for code,size,expected in[(0,0,True),(0,33554432,True),(0,33554433,False),(0,-1,False),(143,0,False),(None,0,False),(0,None,False),(False,0,False),(0,True,False)]:
            self.assertEqual(ENV['accepted'](code,size),expected)

    def test_no_legacy_binding_or_resume(self):
        self.assertIn("SOURCE='969d8ded10c0bf5841d9e3a5c531e922caf4a24a'",RAW)
        self.assertIn('0.1.0-PG548',RAW);self.assertIn('pg549-completed-activate-v5',RAW)
        self.assertNotIn('pg477-completed',RAW);self.assertNotIn('--resume',RAW)
        self.assertIn("len(rows['schubert.batch_runs'])==462",RAW)
        self.assertIn("not pathlib.Path('/var/lib/schubert-nk/maintenance/active').exists()",RAW)
        self.assertIn('pid<>pg_backend_pid()',RAW)


if __name__=='__main__':unittest.main()
