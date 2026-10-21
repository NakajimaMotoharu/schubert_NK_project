import unittest
import inspect
import json
import xml.etree.ElementTree as ET
from unittest.mock import patch
from pathlib import Path
from pyflakes.api import checkPath
import pg6506_current4064_trace as subject
import pg6508_current4064_static_join as joined
import pg6334_current4048_trace_test as previous


class Definition(unittest.TestCase):
    def test_actual_raw_module_xml_and_class_domains_are_not_merged(self):
        qp, qualification = subject.read_qualified()
        total = dict.fromkeys(('LINE','METHOD','CLASS','BRANCH'),0)
        for module in ('protocol','storage','bootstrap','api','web','batch'):
            path = subject.BASE/'PG6490-current4064-cases/coverage'/module/'site/jacoco/jacoco.xml'
            counters = {r.get('type'):int(r.get('missed')) for r in ET.parse(path).getroot().findall('counter')}
            for name in total: total[name] += counters[name]
        self.assertEqual({'LINE':3482,'METHOD':684,'CLASS':38,'BRANCH':714},total)
        self.assertEqual(total,subject.measurement()['remaining'])
        family = sum(c.get('LINE',{}).get('missed',0) for c in qualification['allActualClassCounters'].values())
        self.assertEqual(3490,family)
        self.assertEqual(8,family-total['LINE'])
        self.assertEqual(0,qualification['changedOuterCounters']['web:dev/codex/schubert/nk/web/bootstrap/WebNativeRuntime.class']['LINE']['missed'])
        self.assertEqual(4064,json.loads(qp.read_bytes())['tests'])
    def test_exact4064_run_dimensions_and_prior943_source(self):
        scope = subject.definitions('a'*64, 'b'*64)
        constants = scope['measurement'].__code__.co_consts
        for value in (4064, 612, 'PG6490-six-v1'): self.assertIn(value, constants)
        for value in (4056, 610, 'PG6452-six-v1', 4034, 606): self.assertNotIn(value, constants)
        self.assertIn('PG6506-current943-trace-v1', scope['report'].__code__.co_consts)

    def test_failed_original_is_not_a_missing_result_replay(self):
        with patch.object(Path,'read_bytes',return_value=b'{}'), patch.object(subject.json,'loads',side_effect=[{'actualExit':1},{'actualExit':0}]):
            with self.assertRaisesRegex(ValueError,'genuine original4064'):
                subject.read_qualified()

    def test_static_join_requires_actual4064_and_original27(self):
        constants = joined.definitions()['main'].__code__.co_consts
        self.assertIn(4064,constants)
        self.assertIn('PG6500-web-owned-component-qualification-v5/manifest.json',constants)
        self.assertIn('PG6508-current4064-static-join-v1',constants)
        for path in (subject.__file__,joined.__file__,__file__): self.assertEqual(0,checkPath(path))


raw = inspect.getsource(previous.ActualOriginalCandidate)
for before, after in (
    ('5eb040421ae9ea06ecc70c6eb2e152871c2d0d42','bbbc3f7f13b6858535515dc495ad53839683fb24'),
    ('(943,4048,607,0)','(943,4064,612,0)'),
    ("'LINE':3554","'LINE':3482"),("'METHOD':687","'METHOD':684"),("'BRANCH':723","'BRANCH':714")):
    if before not in raw: raise ValueError('exact actual4064 candidate fixture '+before)
    raw = raw.replace(before,after)
scope = {**vars(previous),'__name__':__name__,'subject':subject}
exec(compile(raw,'<actual4064 current943 candidate>','exec'),scope)
ActualOriginalCandidate = scope['ActualOriginalCandidate']


if __name__ == '__main__': unittest.main()
