"""No private labels/properties/stdout in public projection, no failed case promotion."""
import hashlib
import json
import unittest
from pyflakes.api import checkPath
import pg5058_whole_case_projection as projection


class Cases(unittest.TestCase):
    def test_only_allowed_fields_and_unique_physical_ordinal(self):
        blob = b'<testsuite tests="2"><properties><property name="password" value="PRIVATE_CANARY"/></properties><testcase classname="dev.codex.schubert.nk.batch.ExampleTest" name="PRIVATE_CANARY"/><testcase classname="dev.codex.schubert.nk.batch.ExampleTest" name="PRIVATE_CANARY"/><system-out>PRIVATE_CANARY</system-out></testsuite>'
        values = projection.project_xml('batch', 'TEST-example.xml', blob, hashlib.sha256(blob).hexdigest())
        self.assertEqual(2, len(values))
        self.assertNotEqual(values[0]['testId'], values[1]['testId'])
        self.assertNotIn('PRIVATE_CANARY', json.dumps(values))
        self.assertEqual({'testId', 'module', 'class', 'caseOrdinalInXml', 'caseNameSha256', 'sourceXml', 'xmlSha256', 'result'}, set(values[0]))

    def test_hash_count_and_every_nonpass_marker_refused(self):
        for mark in ('failure', 'error', 'skipped', 'flakyFailure', 'flakyError', 'rerunFailure', 'rerunError'):
            blob = ('<testsuite tests="1"><testcase classname="dev.codex.schubert.ExampleTest" name="a"><' + mark + '/></testcase></testsuite>').encode()
            with self.assertRaises(ValueError):
                projection.project_xml('batch', 'TEST-e.xml', blob, hashlib.sha256(blob).hexdigest())
        for blob in [b'<testsuite tests="1"/>', b'<testsuite tests="0"><testcase classname="dev.codex.schubert.ExampleTest" name="a"/></testsuite>',
                     b'<testsuite tests="1" failures="1"><testcase classname="dev.codex.schubert.ExampleTest" name="a"/></testsuite>']:
            with self.assertRaises(ValueError):
                projection.project_xml('batch', 'TEST-e.xml', blob, hashlib.sha256(blob).hexdigest())
        with self.assertRaises(ValueError):
            projection.project_xml('batch', 'TEST-e.xml', b'notxml', '0' * 64)
        for path in (projection.__file__, __file__):
            self.assertEqual(0, checkPath(path))


if __name__ == '__main__':
    unittest.main()
