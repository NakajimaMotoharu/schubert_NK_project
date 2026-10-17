"""Independent literal Test ID and redaction / unsuccessful original XML refusal."""
import json
import unittest
from pyflakes.api import checkPath
import pg4966_expiry_success_public as role


class PublicExpiry(unittest.TestCase):
    def test_exact_test_id_and_failure_redaction_boundary(self):
        name='dev.codex.schubert.nk.batch.repository.ExpirySuccessfulScopeTest'
        raw=('<testsuite name="'+name+'" tests="1" failures="0" errors="0" skipped="0"><properties><property name="private" value="DO_NOT_EXPORT"/></properties><testcase classname="'+name+'" name="exp4956018Example"/><system-out>DO_NOT_EXPORT</system-out></testsuite>').encode()
        values=role.cases(raw,name)
        self.assertEqual('PT-EXP-4956-018',values[0]['testId']);self.assertTrue(values[0]['newIndependentCase'])
        self.assertNotIn('DO_NOT_EXPORT',json.dumps(values))
        for bad in(raw.replace(b'failures="0"',b'failures="1"'),raw.replace(b'tests="1"',b'tests="2"'),
                   raw.replace(b'exp4956018',b'foreign0018'),raw.replace(b'/><system-out>',b'><flakyFailure/></testcase><system-out>')):
            with self.assertRaises(ValueError):role.cases(bad,name)
        for path in(role.__file__,__file__):self.assertEqual(0,checkPath(path))


if __name__=='__main__':unittest.main()
