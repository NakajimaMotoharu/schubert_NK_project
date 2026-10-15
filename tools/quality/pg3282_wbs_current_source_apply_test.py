"""Bulk measurement rebase, never acceptance; no actual file application in these tests."""
import copy
import json
import unittest
import pg3282_wbs_current_source_apply as subject
import pg3280_wbs_current_source as staged


class WbsMechanicalRebaseTest(unittest.TestCase):
    def test_descriptions_follow_actual_source_run_counts_not_old_baseline(self):
        d = subject.metadata_descriptions('NEW_SOURCE', 'NEW_RUN', 3701, 542, 1643)
        self.assertIn('source=NEW_SOURCE', d['artifactHashMeaning'])
        self.assertIn('selects NEW_RUN', d['artifactHashMeaning'])
        self.assertIn('3701PT/542suite/1643Main', d['measurementMode'])
        self.assertIn('NEW_SOURCE', d['measurementMode'])
        self.assertIn('NEW_RUN', d['measurementMode'])
        self.assertNotIn('retain frozen', d['artifactHashMeaning'])
        self.assertNotIn('PG599', d['measurementMode'])
        self.assertIn('not current source claims', d['measurementMode'])

    def test_root_updates_preserve_other_text_nested_source_and_no_acceptance_change(self):
        text = '{\n  "source":"old",\n  "nested":{"source":"nested-must-stay"},\n  "keep":[1,2],\n  "rows":[{"id":"A","acceptance":{"status":"NOT_ACCEPTED"}}]\n}\n'
        updates = {'source': staged.SOURCE, 'rows': [{'id': 'A', 'acceptance': {'status': 'NOT_ACCEPTED'}, 'missed': 0}], 'newObservation': {'acceptanceGranted': False}}
        result = subject.rewrite_root(text, updates)
        self.assertEqual({**json.loads(text), **updates}, json.loads(result))
        self.assertIn('"nested":{"source":"nested-must-stay"}', result)
        self.assertIn('"keep":[1,2]', result)
        with self.assertRaises(ValueError):
            subject.rewrite_root('{"x":1,"x":2}', {'x': 3})

    @staticmethod
    def fixture():
        acceptance = {'status': 'NOT_ACCEPTED', 'source': None}
        def row(id, status, measured=False):
            r = {'id': id, 'measurementStatus': status, 'acceptance': copy.deepcopy(acceptance), 'evidence': ['historical-proof']}
            if measured:
                r.update(measuredFamilies=1, missed={k: 3 for k in staged.COUNTERS}, measurementOverride={'old': True})
            return r
        snapshot = {'source': 'OLD_BINDING', 'measurementRun': 'OLD_RUN', 'rows': [row('A', 'HOST_GAPS', True), row('B', 'TARGET_ABSENT', True), row('WBS-N05', 'VM_STEP_VERIFIED'), row('WBS-N13', 'VM_STEP_VERIFIED'), row('WBS-CHR-L01', 'BLOCKED_QA051')]}
        inventory = {'artifacts': [
            {'owner': 'A', 'kind': 'JAVA', 'module': 'protocol', 'class': 'p/C'},
            {'owner': 'A', 'kind': 'JAVA', 'module': 'protocol', 'class': 'p/I', 'counterApplicability': 'NO_EXECUTABLE_INTERFACE'},
            {'owner': 'B', 'kind': 'JAVA', 'module': 'protocol', 'class': 'p/MISSING'}]}
        data = {'protocol': {'p/C': {k: [0, 1] for k in staged.COUNTERS}, 'p/I': {k: [0, 0] for k in staged.COUNTERS}}}
        manifest = {'runtimeVerifiedRows': ['WBS-N05', 'WBS-N06', 'WBS-N07', 'WBS-N08', 'WBS-N09', 'WBS-N10', 'WBS-N12', 'WBS-N14']}
        return inventory, snapshot, manifest, data

    def test_same_data_reclassification_preserves_unknown_and_qa_and_all_acceptance(self):
        args = self.fixture(); before = copy.deepcopy(args)
        rows = {r['id']: r for r in subject.reclassified_rows(*args)}
        self.assertEqual(before, args)
        self.assertEqual('HOST_COUNTERS_CLOSED', rows['A']['measurementStatus'])
        self.assertEqual(1, rows['A']['nonExecutableFamilies'])
        self.assertNotIn('measurementOverride', rows['A'])
        self.assertEqual({'old': True}, rows['A']['historicalMeasurements'][0]['measurementOverride'])
        self.assertEqual('TARGET_ABSENT', rows['B']['measurementStatus'])
        self.assertEqual(staged.SOURCE, rows['WBS-N05']['measurementSource'])
        self.assertFalse(rows['WBS-N05']['currentLiveAuthority'])
        self.assertEqual('HISTORICAL_VM_SUCCESS_RECHECK', rows['WBS-N13']['measurementStatus'])
        self.assertEqual('BLOCKED_QA051', rows['WBS-CHR-L01']['measurementStatus'])
        self.assertTrue(all(r['acceptance']['status'] == 'NOT_ACCEPTED' for r in rows.values()))

    def test_no_interface_exclusion_or_unproved_runtime_mapping(self):
        inventory, snapshot, manifest, data = self.fixture(); data['protocol']['p/I']['LINE'] = [0, 1]
        with self.assertRaises(ValueError):
            subject.reclassified_rows(inventory, snapshot, manifest, data)
        inventory, snapshot, manifest, data = self.fixture(); manifest['runtimeVerifiedRows'].append('WBS-CHR-L01')
        with self.assertRaises(ValueError):
            subject.reclassified_rows(inventory, snapshot, manifest, data)


if __name__ == '__main__':
    unittest.main()
