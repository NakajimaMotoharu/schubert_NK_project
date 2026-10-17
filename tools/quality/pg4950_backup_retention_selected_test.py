"""Exact real methods/scope, strict actual result, unchanged Main and format-before-PT."""
import inspect
import re
import unittest
from unittest.mock import patch
from pyflakes.api import check,checkPath
import pg4950_backup_retention_selected as role


class BackupSelected(unittest.TestCase):
    def test_actual_required_three_modules_ten_suites_and_six_independent_methods(self):
        role.validate_selection()
        self.assertEqual({'storage','bootstrap','batch'},set(role.MODULES.values()))
        self.assertEqual(10,len(role.MODULES))
        path=role.ROOT/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/BackupRetentionRejectionTest.java'
        methods=re.findall(r'@Test\s+void\s+([A-Za-z0-9_]+)\(',path.read_text())
        self.assertEqual(6,len(methods));self.assertEqual(6,len(set(methods)))
        self.assertTrue(all(name.startswith('backup495000')for name in methods))

    def test_complete_namespace_no_unexecuted_success_or_main_relabel(self):
        raw=role.source();header=inspect.getsource(role.base).split('\ndef main():',1)[0]
        header+='\nMODULES={}\nMAIN_SOURCE="04bb"\nMETHODS={}\ndef verify_main_bytes(snapshot):raise ValueError("source-only, not a receipt")\n'
        self.assertEqual(0,check(header+'\n'+raw,'<complete selected Backup namespace>'))
        self.assertLess(raw.index('format_command='),raw.index('child = subprocess.Popen'))
        self.assertIn('ptNotRun',raw);self.assertIn("'actualMavenExit': code",raw)
        self.assertIn('actual != expected',raw);self.assertIn('verify_main_bytes(snapshot)',raw)
        self.assertIn("{'LINE','METHOD','BRANCH'}<=set(count)",raw)
        self.assertNotIn('-DfailIfNoTests=false',raw);self.assertNotIn('SystemManagerObservation\' for',raw)
        self.assertIn('spotbugs-maven-plugin:4.10.4.0:check',raw)
        self.assertIn("'productionSource': MAIN_SOURCE",raw);self.assertIn("'testSourceSnapshot': head",raw)
        for path in (role.__file__,__file__):self.assertEqual(0,checkPath(path))

    def test_foreign_full_qualification_cannot_admit_current_main(self):
        from pathlib import Path
        with patch.object(Path,'read_bytes',return_value=b'{"actualExit":1,"result":{}}'):
            with self.assertRaisesRegex(ValueError,'actual original'):role.verify_main_bytes(Path('/no-snapshot-operation'))


if __name__=='__main__':unittest.main()
