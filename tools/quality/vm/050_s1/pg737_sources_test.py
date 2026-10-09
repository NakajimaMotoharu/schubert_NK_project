"""Independent literal current pins and ten true transitive imports/each absence."""
import ast
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from pg737_sources import python_files,java,refs,native,compile_script,receipt


class SourcesTest(unittest.TestCase):
    def test_current_tuple_and_preserved_old_six(self):
        r,n,j,c,p=refs(),native(),java(),compile_script(),receipt()
        for raw in (r,n,p):ast.parse(raw)
        for text in ('len(baseline)==21','==534)','pg736-completed-baseline-v1',
                     'c69d13e43a14525d2e2ec894378e5fd1f6735574f1c63dadadb2306324936f0b',
                     '==129343844863','pg728-native-stop-v1'):
            self.assertIn(text,r)
        for cohort in ('pg664','pg702'):
            for kind in ('tools','verify','existing'):self.assertIn(cohort+'-bootstrap-'+kind+'-v1',r)
        for text in ('1ec19782a1afe22d1de75b05f4cd12b8a8a8a172','74d35361865a32a6b992f93d78d42844e20a5bb286fa4fc4b5e74520fa6305d5',
                     '55ac70e7-0180-4c32-8c91-5a379ebedf24','2026-10-09T03:00:51.014287Z',
                     'ab8895ca-4fb1-440d-b174-bc9f1f27505a','2026-10-09T03:30:40.608594Z'):
            self.assertIn(text,j)
        self.assertIn('pg715-release-v1/api/api.jar',c);self.assertIn('pg715-release-v1/operations/batch.jar',c)
        self.assertIn('$task_work/pg464-code-tools-v2',c)
        self.assertIn("'pg556_parent_receipt.py', 'pg737_parent_receipt.py'",n)
        self.assertIn("JOB='132812'",p);self.assertIn('START=127549297774',p)

    def test_actual_isolated_import_and_each_missing(self):
        files=python_files();self.assertEqual(10,len(files))
        for missing in (None,*files.keys()):
            if missing=='pg737_bootstrap_existing.py':continue
            with self.subTest(missing=missing),tempfile.TemporaryDirectory(prefix='pg737-import-')as directory:
                root=Path(directory)
                for name,raw in {**files,'dbus.py':'# host-only inert stub, never staged\n'}.items():
                    if name==missing:continue
                    fd=os.open(root/name,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o400)
                    with os.fdopen(fd,'w')as f:f.write(raw)
                code='import sys;sys.path.insert(0,'+repr(directory)+');import pg737_bootstrap_existing'
                got=subprocess.run([sys.executable,'-I','-B','-c',code],capture_output=True)
                if missing is None:
                    self.assertEqual(0,got.returncode,got.stderr.decode());self.assertEqual(b'',got.stdout+got.stderr)
                else:
                    self.assertNotEqual(0,got.returncode);self.assertIn(('No module named '+repr(missing[:-3])).encode(),got.stderr)


if __name__=='__main__':unittest.main()
