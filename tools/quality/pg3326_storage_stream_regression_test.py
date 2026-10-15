"""Literal classification tests, including false-positive refusal, no server calls."""
import ast
import unittest
import xml.etree.ElementTree as ET

import pg3326_storage_stream_regression as target


def suite(count, failures=0):
    value = ET.Element('testsuite', tests=str(count), failures=str(failures), errors='0', skipped='0')
    for i in range(count):
        ET.SubElement(value, 'testcase', classname='class', name='case' + str(i))
    return value


class ClassificationTest(unittest.TestCase):
    def test_genuine_before_failure_and_wrong_reason_refused(self):
        value = suite(3, 1)
        case = value[0]; case.set('classname', 'dev.codex.schubert.nk.storage.StorageRootInspectionTest'); case.set('name', target.METHOD)
        error = ET.SubElement(case, 'failure', type='org.opentest4j.AssertionFailedError', message='expected: <0> but was: <2>')
        self.assertEqual(1, target.classify([value], True)['failures'])
        error.set('message', 'compile or wrong assertion')
        with self.assertRaises(ValueError):
            target.classify([value], True)

    def test_expected_failure_not_silently_success(self):
        with self.assertRaises(ValueError):
            target.classify([suite(3)], True)
        value = suite(3, 1); ET.SubElement(value[0], 'failure', type='wrong')
        with self.assertRaises(ValueError):
            target.classify([value], True)

    def test_full_unique_actual_set_and_skip_flaky_refusal(self):
        values = [suite(7) for _ in range(22)] + [suite(9)]
        for i, value in enumerate(values):
            for case in value: case.set('classname', 'class' + str(i))
        self.assertEqual(163, target.classify(values, False)['tests'])
        values[0].set('skipped', '1')
        with self.assertRaises(ValueError): target.classify(values, False)
        values[0].set('skipped', '0'); ET.SubElement(values[0][0], 'flakyFailure')
        with self.assertRaises(ValueError): target.classify(values, False)

    def test_before_option_never_consumes_module_argument(self):
        nodes = list(ast.walk(ast.parse(target.SERVER)))
        insert = [n for n in nodes if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == 'insert']
        self.assertEqual(1, len(insert))
        self.assertEqual(1, ast.literal_eval(insert[0].args[0]))
        self.assertEqual('-Dtest=StorageRootInspectionTest', ast.literal_eval(insert[0].args[1]))
        compile('INPUT={}\n' + target.SERVER, '<test server namespace>', 'exec')


if __name__ == '__main__':
    unittest.main()
