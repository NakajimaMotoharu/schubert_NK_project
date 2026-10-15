"""Independent schema negative tests, no Production PT credit."""
import hashlib
import unittest
import xml.etree.ElementTree as ET
from pg3286_protocol_existing_run_witness import project_suite, server_source


class ExistingRunWitnessTest(unittest.TestCase):
    def test_project_only_names_counts_hashes_not_properties_or_stdout(self):
        root = ET.fromstring('<testsuite name="example.T" tests="1"><properties><property name="secret" value="DO_NOT_EXPORT"/></properties><testcase classname="example.T" name="case1"/><system-out>DO_NOT_EXPORT</system-out></testsuite>')
        result = project_suite(root, 'a' * 64)
        self.assertEqual({'class': 'example.T', 'tests': ['case1'], 'counts': {'tests': 1, 'failures': 0, 'errors': 0, 'skipped': 0}, 'xmlSha256': 'a' * 64}, result)

    def test_reject_counts_failures_flaky_duplicate_foreign_class(self):
        base = '<testsuite name="example.T" tests="1"><testcase classname="example.T" name="case1"/></testsuite>'
        for text in [base.replace('tests="1"', 'tests="2"'), base.replace('/></testsuite>', '><flakyFailure/></testcase></testsuite>'), base.replace('/></testsuite>', '><skipped/></testcase></testsuite>'), base.replace('classname="example.T"', 'classname="foreign.T"'), base.replace('tests="1"', 'tests="0"')]:
            with self.subTest(text=text), self.assertRaises(ValueError):
                project_suite(ET.fromstring(text), 'a' * 64)

    def test_remote_is_readonly_and_hash_literals_remain_exact(self):
        sha = hashlib.sha256(b'fixed').hexdigest()
        code = server_source({'serverManifestSha256': sha, 'qualificationInputs': {'protocol': {'static': sha}}, 'sourceSnapshot': 'b' * 40})
        compile(code, '<read-only witness>', 'exec')
        self.assertIn(repr(sha), code)
        for forbidden in ['subprocess', 'systemctl', 'mvn', '.write_', "open('w'"]:
            self.assertNotIn(forbidden, code)


if __name__ == '__main__':
    unittest.main()
