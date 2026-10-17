"""Literal new Test ID/redaction and skipped/flaky/foreign counterexamples."""
import json
import unittest
from pyflakes.api import checkPath
import pg4954_backup_retention_public as role


class PublicCases(unittest.TestCase):
    def test_allowlist_test_id_not_raw_properties_or_stdout(self):
        name='dev.codex.schubert.nk.batch.file.BackupRetentionRejectionTest'
        raw=('<testsuite name="'+name+'" tests="1" failures="0" errors="0" skipped="0"><properties><property name="private" value="DO_NOT_EXPORT"/></properties><testcase classname="'+name+'" name="backup4950001Example"/><system-out>DO_NOT_EXPORT</system-out></testsuite>').encode()
        value=role.cases(raw,name)
        self.assertEqual('PT-BAK-4950-001',value[0]['testId']);self.assertTrue(value[0]['newIndependentCase'])
        self.assertNotIn('DO_NOT_EXPORT',json.dumps(value))
        for bad in (raw.replace(b'failures="0"',b'failures="1"'),raw.replace(b'tests="1"',b'tests="2"'),raw.replace(b'backup4950001',b'foreign4950001'),raw.replace(b'/><system-out>',b'><flakyFailure/></testcase><system-out>')):
            with self.assertRaises(ValueError):role.cases(bad,name)
        self.assertEqual(0,checkPath(role.__file__));self.assertEqual(0,checkPath(__file__))


if __name__=='__main__':unittest.main()
