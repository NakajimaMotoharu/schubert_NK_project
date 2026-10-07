"""Management-policy regression tests. No Production/VM acceptance credit."""
import copy
import hashlib
import pathlib
import tempfile
import unittest

import wbs_progress_audit as audit


class WbsPolicyTest(unittest.TestCase):
    def cost(self, count=True):
        return {'unit': audit.UNIT, 'low': 1, 'base': 2, 'high': 3,
                'countsInTotal': count, 'actualSpentPp': None, 'actualObservations': [],
                'costScope': 'management fixture', 'estimateBasis': 'fixture', 'confidence': 'LOW'}

    def test_revision_count_is_not_fixed(self):
        originals = [{'id': 'A', 'cost': self.cost()}, {'id': 'B', 'cost': self.cost()}]
        leaves, _ = audit.check_cost_rollup(originals, [], [])
        self.assertEqual(len(leaves), 2)

    def test_parent_child_double_count_rejected(self):
        with self.assertRaisesRegex(ValueError, 'double count'):
            audit.check_cost_rollup([{'id': 'A', 'cost': self.cost()}], [],
                                   [{'id': 'A.01', 'parent': 'A', 'cost': self.cost()}])

    def test_alias_can_reference_without_budget(self):
        zero = self.cost(False)
        zero.update(low=0, base=0, high=0)
        leaves, _ = audit.check_cost_rollup([
            {'id': 'A', 'cost': self.cost()},
            {'id': 'B', 'executionRole': 'REFERENCE_ONLY', 'sharedWorkRef': 'A', 'cost': zero}], [], [])
        self.assertEqual([x['id'] for x in leaves], ['A'])

    def test_alias_cannot_keep_duplicate_budget(self):
        with self.assertRaisesRegex(ValueError, 'alias cost'):
            audit.check_cost_rollup([
                {'id': 'A', 'cost': self.cost()},
                {'id': 'B', 'executionRole': 'REFERENCE_ONLY', 'sharedWorkRef': 'A', 'cost': self.cost()}], [], [])

    def acceptance_fixture(self, path):
        return {'id': 'A', 'dependencies': [], 'acceptanceChecks': [{'id': 'A:contract'}],
                'acceptance': {'status': 'ACCEPTED', 'source': 'fixture-source', 'acceptedBy': 'unit-fixture',
                               'criteriaSatisfied': ['A:contract'],
                               'evidence': [{'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                                             'source': 'fixture-source', 'run': 'management-fixture',
                                             'verifiedChecks': ['A:contract']}]}}

    def test_valid_acceptance_update_allowed(self):
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d) / 'proof.txt'
            p.write_text('management fixture only')
            audit.check_acceptance(self.acceptance_fixture(p), 'fixture-source', {})

    def test_acceptance_requires_real_hash_and_source(self):
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d) / 'proof.txt'
            p.write_text('management fixture only')
            item = self.acceptance_fixture(p)
            with self.assertRaisesRegex(ValueError, 'source'):
                audit.check_acceptance(item, 'other-source', {})
            item['acceptance']['evidence'][0]['sha256'] = '0' * 64
            with self.assertRaisesRegex(ValueError, 'hash'):
                audit.check_acceptance(item, 'fixture-source', {})

    def test_acceptance_with_open_dependency_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d) / 'proof.txt'
            p.write_text('management fixture only')
            item = self.acceptance_fixture(p)
            item['dependencies'] = ['B']
            with self.assertRaisesRegex(ValueError, 'dependency open'):
                audit.check_acceptance(item, 'fixture-source', {'B': {'status': 'NOT_ACCEPTED'}})

    def test_unresolved_external_approval_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d) / 'proof.txt'
            p.write_text('management fixture only')
            item = self.acceptance_fixture(p)
            item['externalPrerequisites'] = ['QA051_RESOLVED']
            with self.assertRaisesRegex(ValueError, 'approval open'):
                audit.check_acceptance(item, 'fixture-source', {})

    def test_cycle_across_parent_and_leaf_rejected(self):
        with self.assertRaisesRegex(ValueError, 'cycle'):
            audit.check_graph({'A': ['A.01'], 'A.01': ['B'], 'B': ['A']})

    def test_new_reset_window_allowed_but_mixed_reset_rejected(self):
        points = [{'id': 'new0', 'timeJST': '2026-10-10T10:00:00+09:00', 'resetEpochSeconds': 200, 'usedPercent': 2},
                  {'id': 'new1', 'timeJST': '2026-10-10T11:00:00+09:00', 'resetEpochSeconds': 200, 'usedPercent': 5}]
        interval = [{'start': 'new0', 'end': 'new1', 'observedPp': 3}]
        self.assertEqual(audit.check_quota_window(points, interval, 200), 3)
        points[1]['resetEpochSeconds'] = 201
        with self.assertRaisesRegex(ValueError, 'mixed reset'):
            audit.check_quota_window(points, interval, 200)

    def observation(self):
        return {'observationId': 'fixture-observation',
                'before': {'timeJST': '2026-10-07T10:00:00+09:00', 'resetEpochSeconds': 200, 'usedPercent': 2},
                'after': {'timeJST': '2026-10-07T11:00:00+09:00', 'resetEpochSeconds': 200, 'usedPercent': 3},
                'observedSharedPp': 1, 'attribution': 'SOLE_WBS', 'allocatedPp': 1,
                'otherChatUsageKnown': True, 'otherChatUsedPp': 0, 'source': 'fixture-source',
                'run': 'management-fixture', 'evidence': ['AGENTS.md']}

    def test_measured_actual_update_allowed(self):
        cost = self.cost()
        cost['actualSpentPp'] = 1
        cost['actualObservations'] = [self.observation()]
        audit.check_actual(cost)
        audit.check_cost_rollup([{'id': 'A', 'cost': cost}], [], [])

    def test_mixed_usage_cannot_be_individual_actual(self):
        cost = self.cost()
        cost['actualSpentPp'] = 1
        cost['actualObservations'] = [self.observation()]
        cost['actualObservations'][0]['otherChatUsageKnown'] = False
        with self.assertRaisesRegex(ValueError, 'unproven'):
            audit.check_actual(cost)

    def test_same_observation_cannot_be_allocated_twice(self):
        cost = self.cost()
        cost['actualSpentPp'] = 1
        cost['actualObservations'] = [self.observation()]
        with self.assertRaisesRegex(ValueError, 'allocated twice'):
            audit.check_cost_rollup([{'id': 'A', 'cost': cost}, {'id': 'B', 'cost': copy.deepcopy(cost)}], [], [])

    def test_no_evidence_is_not_coverage_success(self):
        self.assertEqual(audit.classify([]), 'NO_HOST_MEASUREMENT')
        self.assertEqual(audit.classify([None]), 'TARGET_ABSENT')
        self.assertEqual(audit.classify([[0] * 8]), 'HOST_GAPS')


if __name__ == '__main__':
    unittest.main()
