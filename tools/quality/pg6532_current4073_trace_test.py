"""Trace definition checks separate from actual post-qualification assertions; no skipped tests."""
import inspect
import json
import unittest
import xml.etree.ElementTree as ET
from unittest.mock import patch
from pyflakes.api import checkPath
import pg6532_current4073_trace as subject


class Definition(unittest.TestCase):
    def test_exact_dimensions_and_current_candidate_history(self):
        scope = subject.definitions('a'*64, 'b'*64)
        constants = scope['measurement'].__code__.co_consts
        for value in (4073, 614, 'PG6524-six-v1'):
            self.assertIn(value, constants)
        for value in (4064, 612, 4034, 606, 'PG6490-six-v1'):
            self.assertNotIn(value, constants)
        self.assertIn('PG6532-current943-trace-v1', scope['report'].__code__.co_consts)
        self.assertIn('e45cfd31c8d610922f4e9432cc1cf11fa9b48338',
                      inspect.getsource(subject.candidates))
        for path in (subject.__file__, __file__):
            self.assertEqual(0, checkPath(path))

    def test_unqualified_original_cannot_publish(self):
        with patch.object(subject, 'read_qualified', side_effect=ValueError('original pending')):
            with self.assertRaisesRegex(ValueError, 'pending'):
                subject.measurement()


class ActualOriginal(unittest.TestCase):
    def test_source_module_counter_domain_is_actual_xml_not_union(self):
        qp, q = subject.read_qualified(); measured = subject.measurement()
        total = dict.fromkeys(('LINE', 'METHOD', 'CLASS', 'BRANCH'), 0)
        for module in ('protocol', 'storage', 'bootstrap', 'api', 'web', 'batch'):
            path = subject.ROOT/q['coverageRoot']/module/'site/jacoco/jacoco.xml'
            counters = {r.get('type'): int(r.get('missed')) for r in ET.parse(path).getroot().findall('counter')}
            for key in total:
                total[key] += counters[key]
        self.assertEqual(total, measured['remaining'])
        self.assertEqual((4073, 614), (measured['tests'], measured['suites']))
        self.assertEqual(subject.SOURCE, json.loads(qp.read_bytes())['productionSource'])
        self.assertFalse(measured['nativeQualified'])
        self.assertFalse(measured['formalAccepted'])


if __name__ == '__main__':
    unittest.main()
