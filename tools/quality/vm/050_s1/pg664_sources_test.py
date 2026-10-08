"""BOOT664001 real isolated non-operational imports + missing transitive dependency."""
import ast
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from pg664_sources import python_files,java,refs,native,compile_script


class Test(unittest.TestCase):
    def test_isolated_import_and_missing_dependency(self):
        # dbus is unavailable on host; the module import only stores names, no operation
        # is invoked. Its stub contains no surface and therefore cannot start/ref a Unit.
        with tempfile.TemporaryDirectory(prefix='pg664-import-')as directory:
            root=Path(directory)
            for name,raw in {**python_files(),'dbus.py':'# Nonoperational host-only stub\n'}.items():
                fd=os.open(root/name,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o400)
                with os.fdopen(fd,'w')as f:f.write(raw)
            code="import sys;sys.path.insert(0,"+repr(str(root))+");import pg664_bootstrap_existing"
            good=subprocess.run([sys.executable,'-I','-B','-c',code],capture_output=True)
            self.assertEqual(good.returncode,0,good.stderr.decode());self.assertEqual(good.stdout,b'');self.assertEqual(good.stderr,b'')
            # A new isolated directory omits exactly the historical helper dependency.
            with tempfile.TemporaryDirectory(prefix='pg664-import-missing-')as missing:
                for name,raw in {**python_files(),'dbus.py':'# No operations\n'}.items():
                    if name=='pg556_parent_receipt.py':continue
                    fd=os.open(Path(missing)/name,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o400)
                    with os.fdopen(fd,'w')as f:f.write(raw)
                code="import sys;sys.path.insert(0,"+repr(missing)+");import pg664_bootstrap_existing"
                bad=subprocess.run([sys.executable,'-I','-B','-c',code],capture_output=True)
                self.assertNotEqual(bad.returncode,0)
                self.assertIn(b"No module named 'pg556_parent_receipt'",bad.stderr)

    def test_current_parent_and_new_only_paths(self):
        r=refs();n=native();ast.parse(r);ast.parse(n)
        self.assertIn('from pg664_parent_join import completed_journal',r)
        self.assertIn('from pg664_parent_receipt import completed',python_files()['pg664_parent_join.py'])
        self.assertIn("'pg556_parent_receipt.py', 'pg664_parent_receipt.py'",n)
        self.assertIn('pg664-bootstrap-tools-v1',n)
        self.assertIn('Pg664BootstrapExisting',java())
        self.assertIn('pg631-release-v1',compile_script())
        self.assertIn("prior['actualExit'] == 0 and prior['toolHashes'] == hashes",n)
        self.assertNotIn('pg662-bootstrap-tools-v1',n)


if __name__=='__main__':unittest.main()
