import copy
import json
import unittest

import pg3288_layout_acceptance as subject


class IndividualAcceptanceTest(unittest.TestCase):
    def test_change_one_complete_task_preserves_other_bytes(self):
        text = '{\n "tasks":[\n    {"id": "WBS-P001-02", "acceptance": {"status":"NOT_ACCEPTED"}},\n    {"id": "other", "keep":"original bytes"}\n ]\n}\n'
        changed = {'id': subject.ID, 'acceptance': {'status': 'ACCEPTED'}}
        value = subject.one_line_task(text, subject.ID, changed)
        self.assertEqual(changed, json.loads(value)['tasks'][0])
        self.assertIn('    {"id": "other", "keep":"original bytes"}', value)
        compact = text.replace('"id": "', '"id":"')
        self.assertEqual(json.loads(value), json.loads(subject.one_line_task(compact, subject.ID, changed)))
        with self.assertRaises(ValueError):
            subject.one_line_task(text, 'missing', changed)
        with self.assertRaises(ValueError):
            subject.one_line_task(text, subject.ID, {**changed, 'newKey': True})

    def test_actual_compact_master_line_and_duplicate_reject(self):
        text = (subject.audit.PMO / '481_PGPT詳細WBS.json').read_text()
        original = next(t for t in json.loads(text)['tasks'] if t['id'] == subject.ID)
        changed = copy.deepcopy(original); changed['acceptance']['status'] = 'IN_PROGRESS'
        result = json.loads(subject.one_line_task(text, subject.ID, changed))
        expected = json.loads(text)
        next(t for t in expected['tasks'] if t['id'] == subject.ID)['acceptance']['status'] = 'IN_PROGRESS'
        self.assertEqual(expected, result)
        repeated = json.dumps(original) + ',\n' + json.dumps(original) + '\n'
        with self.assertRaises(ValueError):
            subject.one_line_task(repeated, subject.ID, changed)

    def fixture(self):
        canonical = {'actualExit': 0, 'productionSource': subject.SOURCE, 'layoutTuples': 64, 'fieldRows': 389, 'nonemptyAreas': 74, 'namedMappings': 64, 'expectedGeneratedFromProduction': False}
        witness = subject.audit.read_json(subject.ROOT / subject.PUBLIC / 'test-witness.json')
        master = subject.audit.read_json(subject.audit.PMO / '481_PGPT詳細WBS.json')
        snapshot = subject.audit.read_json(subject.audit.PMO / '486_WBS現行実績.json')
        task = next(t for t in master['tasks'] if t['id'] == subject.ID)
        row = next(r for r in snapshot['rows'] if r['id'] == subject.ID)
        # Current acceptance is deliberately reset in this isolated validation fixture.
        task['acceptance']['status'] = 'NOT_ACCEPTED'
        return canonical, witness, task, row

    def test_actual_proof_complete_then_reject_wrong_source_oracle_gap_missing_test(self):
        args = self.fixture(); subject.check_inputs(*args)
        for target, key, value in [(0, 'productionSource', 'foreign'), (0, 'fieldRows', 388), (0, 'expectedGeneratedFromProduction', True), (1, 'actualExit', 1), (1, 'testsReissued', 1), (2, 'dependencies', ['open'])]:
            bad = copy.deepcopy(args); bad[target][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                subject.check_inputs(*bad)
        bad = copy.deepcopy(args)
        suite = next(s for s in bad[1]['suites'] if s['class'].endswith('LayoutMetadataTest'))
        suite['tests'].remove('registryMatchesIndependentUi233Catalog')
        with self.assertRaises(ValueError):
            subject.check_inputs(*bad)


if __name__ == '__main__':
    unittest.main()
