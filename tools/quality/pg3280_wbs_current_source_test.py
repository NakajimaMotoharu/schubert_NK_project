"""Management preparation contracts; synthetic fixtures grant no PG/PT acceptance."""
import copy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET
import pg3280_wbs_current_source as subject
import wbs_progress_audit as audit


class CurrentSourceMeasurementTest(unittest.TestCase):
    @staticmethod
    def fixture():
        counts = dict(zip(subject.MODULES, [84, 163, 298, 969, 888, 1299]))
        full = {'actualExit': 0, 'result': {'actualExit': 0, 'productionSource': subject.SOURCE,
                 'tests': 3701, 'suites': 542, 'mainClasses': 1643, 'FESFlakyNotRun': 0,
                 'staticSixModules': 0, 'modules': {m: {'tests': n} for m, n in counts.items()}}}
        native = {'actualExit': 0, 'result': {'actualExit': 0, 'productionSource': subject.SOURCE,
                   'qualifiedFullTests': 3701, 'qualifiedNativeStreams': 28, 'distinctSessions': 28,
                   'mainClassesIdentical': 1643, 'allResourceMetaMembersIdentical': 79,
                   'VMOperations': 0, 'oldSourceNativeImported': 0,
                   'xmlHashes': {m: 'a' * 64 for m in counts}, 'moduleCounters': {m: {} for m in counts}}}
        return full, native

    def test_exact_schema_and_no_input_mutation(self):
        full, native = self.fixture(); before = copy.deepcopy((full, native))
        subject.authorities(full, native)
        self.assertEqual(before, (full, native))

    def test_old_source_count_failed_missing_partial_and_boolean_refused(self):
        for key, value in [('productionSource', '0' * 40), ('qualifiedFullTests', 3699),
                           ('qualifiedNativeStreams', 27), ('VMOperations', 1)]:
            full, native = self.fixture(); native['result'][key] = value
            with self.assertRaises(ValueError):
                subject.authorities(full, native)
        full, native = self.fixture(); full['actualExit'] = False
        with self.assertRaises(ValueError):
            subject.authorities(full, native)
        full, native = self.fixture(); full['result']['FESFlakyNotRun'] = 1
        with self.assertRaises(ValueError):
            subject.authorities(full, native)
        full, native = self.fixture(); del native['result']['xmlHashes']['batch']
        with self.assertRaises(ValueError):
            subject.authorities(full, native)
        full, native = self.fixture(); del native['result']['qualifiedFullTests']
        with self.assertRaises(KeyError):
            subject.authorities(full, native)

    def test_session_redaction_preserves_every_other_counter_and_node(self):
        raw = b'<report name="synthetic"><sessioninfo id="RAW_TECHNICAL_ID" start="1" dump="2"/><package name="p"><class name="p/C"><method name="work" desc="()V" line="1"/></class><sourcefile name="C.java"><line nr="1" mi="0" ci="2" mb="0" cb="1"/></sourcefile></package><counter type="INSTRUCTION" missed="0" covered="9"/><counter type="COMPLEXITY" missed="0" covered="2"/><counter type="LINE" missed="0" covered="1"/><counter type="METHOD" missed="0" covered="1"/><counter type="CLASS" missed="0" covered="1"/><counter type="BRANCH" missed="0" covered="2"/></report>'
        expected = {'LINE': {'missed': 0, 'covered': 1}, 'METHOD': {'missed': 0, 'covered': 1},
                    'CLASS': {'missed': 0, 'covered': 1}, 'BRANCH': {'missed': 0, 'covered': 2},
                    'classByteMismatch': 0, 'formal': False}
        public, proof = subject.redact_report(raw, expected)
        self.assertNotIn(b'RAW_TECHNICAL_ID', public)
        self.assertIn(b'SHA256:', public)
        self.assertEqual(subject.semantic_report(ET.fromstring(raw)), subject.semantic_report(ET.fromstring(public)))
        self.assertEqual(1, proof['redactedSessionRecords'])
        self.assertNotEqual(proof['rawSha256'], proof['publicSha256'])
        for key in subject.COUNTERS:
            wrong = copy.deepcopy(expected); wrong[key]['missed'] = 1
            with self.assertRaises(ValueError):
                subject.redact_report(raw, wrong)
            missing = copy.deepcopy(expected); del missing[key]
            with self.assertRaises(ValueError):
                subject.redact_report(raw, missing)
        for key, value in [('classByteMismatch', 1), ('formal', True)]:
            with self.assertRaises(ValueError):
                subject.redact_report(raw, {**expected, key: value})
        with self.assertRaises(ValueError):
            subject.redact_report(raw.replace(b'INSTRUCTION', b'UNKNOWN'), expected)

    def test_download_outside_seven_fixed_leaves_rejected_before_authentication(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(subject.lan_server, 'pinned_key', side_effect=AssertionError('must not authenticate')):
            for name in ['../manifest.safe.json', 'backup.sql', 'key', 'api-union.xml;true']:
                with self.assertRaises(ValueError):
                    subject.fetch_fixed(name, Path(directory) / 'target')

    def test_relative_coverage_is_root_bound_and_old_absolute_remains_unchanged(self):
        self.assertEqual(audit.ROOT / 'evidence/fixture/coverage', audit.coverage_root('evidence/fixture/coverage'))
        absolute = '/home/mini/codex/project1/work/pgpt-runs/PG379/pg540-six-host-v1'
        self.assertEqual(Path(absolute), audit.coverage_root(absolute))
        for invalid in ['', '../outside', 'evidence/../outside', 'evidence/./scope', 'evidence\\scope']:
            with self.assertRaises(ValueError):
                audit.coverage_root(invalid)


if __name__ == '__main__':
    unittest.main()
