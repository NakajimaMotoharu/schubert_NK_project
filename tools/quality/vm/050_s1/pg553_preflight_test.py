"""Current source/whole table/predicate binding; no actual data or VM action."""
import ast
import pathlib
import re
import stat
import tempfile
from pathlib import Path
import unittest
from pg553_precondition import successful_preflight,SOURCE,DIGEST

R=Path(__file__).resolve().parent;RAW=(R/'pg553_newrun_preflight.py').read_text()
N=next(n for n in ast.parse(RAW).body if isinstance(n,ast.FunctionDef)and n.name=='accepted')
ENV={};exec(compile(ast.Module(body=[N],type_ignores=[]),'<literal output oracle>','exec'),ENV)
BACK={'pathlib':pathlib,'re':re,'stat':stat}
exec(compile(ast.Module(body=[n for n in ast.parse(RAW).body if isinstance(n,ast.FunctionDef)and n.name in('require','backup_upper_bound')],type_ignores=[]),'<independent retention upper bound>','exec'),BACK)


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

    def test_retention_upper_bound_independent_nine_fixture(self):
        with tempfile.TemporaryDirectory()as t:
            root=Path(t)
            for i in range(9):
                p=root/f'20261008-120000-{i:08x}-0000-0000-0000-000000000000';p.mkdir()
                names=['schubert_nk.dump']
                if i<4:names+=['MANIFEST.json','config.tar','credentials.tar.age']
                if i==8:names+=['negative.dump']
                for name in names:(p/name).touch()
            got=BACK['backup_upper_bound'](root)
            self.assertEqual((len(got['oldNames']),got['eligibleUpperBound'],got['protectedLowerBound'],got['maximumEligibleAfterNew'],got['expectedRetentionDeletes']),(9,4,5,5,0))
            first=next(p for p in root.iterdir()if p.name.startswith('20261008-120000-00000000'))
            (first/'config.tar').unlink();(first/'config.tar').symlink_to(first/'schubert_nk.dump')
            self.assertEqual(BACK['backup_upper_bound'](root)['eligibleUpperBound'],3)
            (root/'unknown').mkdir()
            self.assertEqual(BACK['backup_upper_bound'](root)['protectedLowerBound'],7)

    def test_retention_boundary_and_bad_input(self):
        for bad in(None,{},'path'):
            with self.assertRaises(ValueError):BACK['backup_upper_bound'](bad)
        with tempfile.TemporaryDirectory()as t:
            root=Path(t)
            with self.assertRaises(ValueError):BACK['backup_upper_bound'](root)
            for i in range(7):
                p=root/f'20261008-120000-{i:08x}-0000-0000-0000-000000000000';p.mkdir()
                for n in('MANIFEST.json','config.tar','credentials.tar.age','schubert_nk.dump'):(p/n).touch()
            with self.assertRaises(ValueError):BACK['backup_upper_bound'](root)
            for p in list(root.iterdir())[:1]:(p/'MANIFEST.json').unlink()
            self.assertEqual(BACK['backup_upper_bound'](root)['maximumEligibleAfterNew'],7)

    def test_successor_typed_success_and_negatives(self):
        good={'run':'PG553-newrun-preflight-v2','snapshot24':True,'starts0':True,'source':SOURCE,'manifestSha256':DIGEST,'beforeSha256':'a'*64}
        self.assertTrue(successful_preflight(b'0\n',good))
        for code in(None,0,False,b'1\n',b'143\n',b'0',b'00\n'):
            self.assertFalse(successful_preflight(code,good))
        for value in(None,[],False):self.assertFalse(successful_preflight(b'0\n',value))
        for key in good:
            for value in(None,False,1,'foreign'):
                self.assertFalse(successful_preflight(b'0\n',{**good,key:value}))
            missing=good.copy();del missing[key];self.assertFalse(successful_preflight(b'0\n',missing))
        host=ast.parse((R/'pg553_oracle_host.py').read_text())
        guard=next(n.lineno for n in host.body if isinstance(n,ast.Assert)and 'successful_preflight' in ast.unparse(n))
        mutations=[n.lineno for n in host.body if isinstance(n,ast.Expr)and 'subprocess.run' in ast.unparse(n)]
        self.assertTrue(all(line>guard for line in mutations))


if __name__=='__main__':unittest.main()
