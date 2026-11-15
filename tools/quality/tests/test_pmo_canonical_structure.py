"""BUG3084/YKT2557: metadata only; no product, network, job or real event mutation."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import Mock, patch

from pmo_group_context import collect_canonical_nodes, validate_implementation_artifacts

ROOT = Path(__file__).resolve().parents[3]
PMO = ROOT / 'documents/400_PGPT/470_PMO'


def actual_plans():
    return [json.loads((PMO / name).read_text()) for name in
            ['481_PGPT詳細WBS.json', '484_WBSコスト枠・細分化.json']]


class CanonicalStructureTest(unittest.TestCase):
    def test_actual276_structure_retains_parent_and_exact_children(self):
        nodes = collect_canonical_nodes(actual_plans())
        self.assertEqual(276, len(nodes))
        self.assertEqual(['WBS-P017-07.01', 'WBS-P017-07.02', 'WBS-P017-07.03'],
                         nodes['WBS-P017-07']['children'])
        for child in ['WBS-P017-07.01', 'WBS-P017-07.02', 'WBS-P017-07.03']:
            self.assertEqual('WBS-P017-07', nodes[child]['parent'])
            self.assertFalse(nodes[child].get('children'))

    def test_history_same_id_and_nested_criteria_are_not_structural_nodes(self):
        plans = actual_plans()
        before = collect_canonical_nodes(plans)
        plans[1]['planningBaseline'] = {
            'nested': [{'id': 'WBS-P017-07', 'revised': {'base': 999}}],
            'fake': {'id': 'WBS-FAKE', 'children': []}}
        plans[0]['tasks'][0]['acceptanceChecks'] = [{'id': 'WBS-FAKE-CRITERION'}]
        after = collect_canonical_nodes(plans)
        self.assertEqual(set(before), set(after))
        self.assertEqual(['WBS-P017-07.01', 'WBS-P017-07.02', 'WBS-P017-07.03'],
                         after['WBS-P017-07']['children'])

    def test_duplicate_actual_ids_fail_instead_of_last_writer_wins(self):
        for duplicate in [{'id': 'WBS-X'}, {'id': 'WBS-X', 'children': ['WBS-X.1']}]:
            with self.subTest(duplicate=duplicate), self.assertRaises(ValueError):
                collect_canonical_nodes([{'tasks': [{'id': 'WBS-X'}]},
                                         {'children': [duplicate]}])

    def test_missing_or_malformed_structural_arrays_are_rejected(self):
        for plan in [None, {}, {'tasks': None}, {'children': {}}, {'tasks': ['WBS-X']}]:
            with self.subTest(plan=plan), self.assertRaises(ValueError):
                collect_canonical_nodes([plan])

    def test_invalid_id_and_child_array_are_rejected(self):
        for node in [{}, {'id': None}, {'id': 'NOT-WBS'}, {'id': 'WBS-X:quality'},
                     {'id': 'WBS-X', 'children': 'WBS-Y'},
                     {'id': 'WBS-X', 'children': [{'id': 'WBS-Y'}]}]:
            with self.subTest(node=node), self.assertRaises(ValueError):
                collect_canonical_nodes([{'tasks': [node]}])

    def test_actual_cleanup_owner_binds_only_real_descendant_leaf(self):
        plans = actual_plans()
        nodes = collect_canonical_nodes(plans)
        rows = json.loads((PMO / '485_WBS網羅性・受入対応.json').read_text())['artifacts']
        artifact = 'src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/repository/CleanupKind.java'
        config = dict(category='IMPLEMENTATION', kind='ADDITIONAL_FINDING',
                      implementationArtifactPaths=[artifact],
                      wbsLeafIds=['WBS-P017-07.02'],
                      implementationOwnerLeafBindings={'WBS-P017-07': ['WBS-P017-07.02']})
        validate_implementation_artifacts(config, rows, nodes)
        for leaf in ['WBS-P017-07', 'WBS-P017-02.01', 'WBS-UNKNOWN', 'WBS-P017-07.02:quality']:
            bad = copy.deepcopy(config)
            bad['wbsLeafIds'] = [leaf]
            bad['implementationOwnerLeafBindings']['WBS-P017-07'] = [leaf]
            with self.subTest(leaf=leaf), self.assertRaises(ValueError):
                validate_implementation_artifacts(bad, rows, nodes)

    def test_metrics_guard_rejects_parent_and_admits_child_before_blocked_event_open(self):
        path = ROOT / 'tools/quality/vm/050_s1/pg998_metrics.py'
        spec = importlib.util.spec_from_file_location('pgpt_tool_only_metrics', path)
        metrics = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(metrics)
        blocked = Mock()
        blocked.open.side_effect = RuntimeError('TOOL_TEST_BLOCKED_BEFORE_EVENT_WRITE')
        with patch.object(metrics, 'EVENTS', blocked), patch.object(
                metrics, 'estimate_identity', return_value=('tool-test', 'a' * 64)):
            for leaf in ['WBS-P017-07', 'WBS-UNKNOWN', 'WBS-P017-07.02:quality']:
                with self.subTest(leaf=leaf), self.assertRaisesRegex(ValueError, 'actual 481/484 leaf'):
                    metrics.append('TOOL-ONLY', 'GROUP_START', dict(wbsLeafIds=[leaf]))
            blocked.open.assert_not_called()
            with self.assertRaisesRegex(RuntimeError, 'TOOL_TEST_BLOCKED_BEFORE_EVENT_WRITE'):
                metrics.append('TOOL-ONLY', 'GROUP_START', dict(wbsLeafIds=['WBS-P017-07.02']))
            blocked.open.assert_called_once_with('a+b')

    def test_input_plans_are_not_mutated_and_shared_budget_roots_are_present(self):
        plans = actual_plans()
        before = copy.deepcopy(plans)
        nodes = collect_canonical_nodes(plans)
        self.assertEqual(before, plans)
        for node in ['WBS-K01', 'WBS-K02', 'WBS-K03']:
            self.assertEqual(node, nodes[node]['id'])


if __name__ == '__main__':
    unittest.main()
