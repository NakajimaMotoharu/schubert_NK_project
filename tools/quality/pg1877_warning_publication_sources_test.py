"""Independent epoch/marker/cohort/phase vectors and actual kernel exchange oracle."""
import ast
import hashlib
import os
from pathlib import Path
import tempfile
import types
import unittest
from unittest.mock import patch
from pyflakes.api import check
from pg1877_warning_publication_sources import sources
from pg1877_unit_exchange_contract import rename,UNIT,PART,PRIVATE

EPOCH=b'NKEPOCH1\nstate=INVALID\nboot_id=3d69f5af-6bac-46b1-a540-7591c4a79a0d\nepoch_id=11111111-2222-4333-8444-555555555555\nrun_id=4148e3e8-f107-431a-ab27-d6e6d1f1772e\ncutoff_utc=2026-10-12T18:20:32.598894Z\nactivation_id=9adbf05a-61d0-408b-b51d-ab19c7e5b16a\npermit_sha256=-\n'


class Sources(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.actual=sources()

    def test_actual_epoch_and_wrong_roles(self):
        module=types.ModuleType('actual_warning_epoch')
        exec(self.actual['pg1877_ordinary_publication_contract.py'],module.__dict__)
        self.assertEqual(EPOCH,module.epoch_bytes('11111111-2222-4333-8444-555555555555'))
        self.assertIsNone(module.canonical_epoch(EPOCH))
        for value in [None,b'',EPOCH+b'\n',EPOCH.replace(b'INVALID',b'ISSUED'),EPOCH.replace(b'4148e3e8',b'0be226b1')]:
            with self.assertRaises(ValueError):module.canonical_epoch(value)

    def test_exact_literal_and_complete_actual_import_graph(self):
        java=self.actual['Pg1877OrdinaryPublication.java'];raw=self.actual['pg1877_input_preflight.py']
        prints=[n.args[0].value for n in ast.walk(ast.parse(raw))if isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id=='print'and n.args and isinstance(n.args[0],ast.Constant)]
        self.assertEqual(['PG1877_INPUT_CLOSURE_READY'],prints)
        self.assertIn('"PG1877_INPUT_CLOSURE_READY\\n".getBytes(StandardCharsets.US_ASCII)',java)
        for name,body in self.actual.items():
            if name.endswith('.py'):
                self.assertEqual(0,check(body,'<actual '+name+'>'))
                for node in ast.walk(ast.parse(body)):
                    mods=[a.name for a in node.names]if isinstance(node,ast.Import)else[node.module]if isinstance(node,ast.ImportFrom)else[]
                    for mod in mods:
                        if mod.startswith('pg'):self.assertIn(mod.split('.')[0]+'.py',self.actual)

    def test_same_owner_unit_after_signed_current_before_normal_release(self):
        j=self.actual['Pg1877OrdinaryPublication.java'];r=self.actual['pg1877_native_refs.py']
        begin=j.index('static void publish(')
        self.assertLess(j.index('verify(candidate)',begin),j.index('refs.check("unit")',begin))
        self.assertLess(j.index('refs.check("unit")',begin),j.index('refs.check("reload")',begin))
        self.assertLess(j.index('refs.check("reload")',begin),j.index('directory.close()',begin))
        self.assertIn('done.outcome()==MaintenanceCompletion.Outcome.WARNING',j)
        self.assertIn("if action in ['terminal','release']:require(unit_phase=='reloaded')",r)
        self.assertIn("'10'if unit_phase=='reloaded'else''",r)
        self.assertIn("unit_exchange.verify()",r)
        self.assertIn("pg1874-warning-candidate-host-ro-v1/after.private.json",r)
        self.assertNotIn('reset-failed',j+r)

    def test_kernel_exchange_and_noreplace_preserves_old_inode_bytes(self):
        with tempfile.TemporaryDirectory()as root:
            d=Path(root);(d/'private').mkdir();(d/UNIT).write_bytes(b'old independent vector');(d/PART).write_bytes(b'new independent vector')
            a=os.open(d,os.O_RDONLY|os.O_DIRECTORY);b=os.open(d/'private',os.O_RDONLY|os.O_DIRECTORY)
            try:
                old=(d/UNIT).stat().st_ino;new=(d/PART).stat().st_ino
                rename(a,PART,a,UNIT,2)
                self.assertEqual(new,(d/UNIT).stat().st_ino);self.assertEqual(old,(d/PART).stat().st_ino)
                rename(a,PART,b,PRIVATE,1)
                self.assertEqual(old,(d/'private'/PRIVATE).stat().st_ino)
                self.assertEqual(hashlib.sha256(b'old independent vector').hexdigest(),hashlib.sha256((d/'private'/PRIVATE).read_bytes()).hexdigest())
                self.assertEqual(b'new independent vector',(d/UNIT).read_bytes());self.assertFalse((d/PART).exists())
                (d/PART).write_bytes(b'foreign')
                with self.assertRaises(OSError):rename(a,PART,b,PRIVATE,1)
                self.assertEqual(b'old independent vector',(d/'private'/PRIVATE).read_bytes())
            finally:os.close(a);os.close(b)

    def test_foreign_null_unknown_rename_refused_before_native(self):
        with patch('pg1877_unit_exchange_contract.ctypes.CDLL')as call:
            for args in [(None,PART,2,UNIT,2),(True,PART,2,UNIT,2),(1,'other',2,UNIT,2),(1,PART,2,UNIT,0),(1,PART,2,PRIVATE,2)]:
                with self.assertRaises(ValueError):rename(*args)
            call.assert_not_called()


if __name__=='__main__':unittest.main()
