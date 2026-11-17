"""Fixed metadata trust-boundary examples, no source/byte/process/private IO."""
import copy
import hashlib
import json
import unittest
from wbs_preparation_registry import verify

A = 'src/example/src/main/java/A.java'
B = 'src/example/src/main/java/B.java'
TASKS = [{'id': 'WBS-X', 'executionRole': 'WORK'}, {'id': 'WBS-Y', 'executionRole': 'WORK'}]


def independent_sha(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                    separators=(',', ':')).encode()).hexdigest()


def fixture():
    old = [dict(path=A, owner='WBS-X', costOwner='WBS-X', kind='PROGRAM',
                sha256='a'*64, acceptance='UNASSESSED', basis='old')]
    current = copy.deepcopy(old) + [dict(path=B, owner='WBS-X', costOwner='WBS-X',
                                       kind='PROGRAM', sha256='b'*64, acceptance='NOT_RUN_HOLD')]
    binding = dict(schema='WBS_PREPARATION_REGISTRY_SEPARATION_V1', runtimeQualified=False,
                   wholeAcceptance=False, sourceBytesRecomputed=False, newAcceptance=0,
                   effortRate=None, legacySemanticSha256=independent_sha(old),
                   registrySemanticSha256=independent_sha(current), registeredAdditions=[B],
                   legacyFieldUpdates={}, retainedRetiredHistoricalPaths=[])
    return old, current, binding


class RegistryTest(unittest.TestCase):
    def test_preserves_legacy_and_held_new_row_without_runtime_acceptance(self):
        old, current, b = fixture()
        result = verify(old, current, b, TASKS, {A, B}, {})
        self.assertEqual((1, 2, 1), (result['legacyRows'], result['preparationRows'], result['registeredAdditions']))
        self.assertIs(False, result['runtimeQualified'])
        self.assertEqual('NOT_RUN_HOLD', current[1]['acceptance'])

    def test_frozen_legacy_mutation_is_rejected_even_if_current_is_unchanged(self):
        old, current, b = fixture(); old[0]['sha256'] = 'c'*64
        with self.assertRaisesRegex(ValueError, 'frozen legacy changed'):
            verify(old, current, b, TASKS, {A, B}, {})

    def test_current_changes_must_be_recorded_and_allow_only_unqualified_hash_or_basis(self):
        old, current, b = fixture(); current[0]['sha256'] = 'c'*64
        b['registrySemanticSha256'] = independent_sha(current)
        with self.assertRaisesRegex(ValueError, 'exact recorded'):
            verify(old, current, b, TASKS, {A, B}, {})
        b['legacyFieldUpdates'] = {A: {'sha256': {'legacy': 'a'*64, 'registered': 'c'*64}}}
        self.assertEqual(1, verify(old, current, b, TASKS, {A, B}, {})['currentHashOrBasisUpdates'])
        current[0]['changeEvidence'] = 'new optional annotation'
        b['registrySemanticSha256'] = independent_sha(current)
        self.assertEqual(1, verify(old, current, b, TASKS, {A, B}, {})['currentHashOrBasisUpdates'])

    def test_legacy_identity_removal_and_duplicate_are_rejected(self):
        for mode in ['owner', 'kind', 'removed', 'duplicate']:
            old, current, b = fixture()
            if mode == 'owner': current[0]['owner'] = 'WBS-Y'
            elif mode == 'kind': current[0]['kind'] = 'CONFIG'
            elif mode == 'removed': current.pop(0)
            else: current.append(copy.deepcopy(current[0]))
            b['registrySemanticSha256'] = independent_sha(current)
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                verify(old, current, b, TASKS, {A, B}, {})

    def test_unknown_hash_acceptance_owner_and_unrecorded_snapshot_are_rejected(self):
        for field, value in [('sha256', None), ('acceptance', 'ACCEPTED'), ('owner', 'WBS-Z')]:
            old, current, b = fixture(); current[1][field] = value
            b['registrySemanticSha256'] = independent_sha(current)
            with self.subTest(field=field), self.assertRaises(ValueError):
                verify(old, current, b, TASKS, {A, B}, {})
        old, current, b = fixture(); current[1]['sha256'] = 'c'*64
        with self.assertRaisesRegex(ValueError, 'unrecorded registry'):
            verify(old, current, b, TASKS, {A, B}, {})

    def test_absent_new_filename_cannot_be_relabelled_retired(self):
        old, current, b = fixture()
        with self.assertRaises(ValueError): verify(old, current, b, TASKS, {A}, {})
        b['retainedRetiredHistoricalPaths'] = [B]
        with self.assertRaisesRegex(ValueError, 'new artifact absent'):
            verify(old, current, b, TASKS, {A}, {})

    def test_separate_cost_owner_needs_exact_pinned_existing_evidence(self):
        old, current, b = fixture(); current[1]['costOwner'] = 'WBS-Y'
        b['registrySemanticSha256'] = independent_sha(current)
        with self.assertRaisesRegex(ValueError, 'lacks pinned'):
            verify(old, current, b, TASKS, {A, B}, {})
        proof = dict(actualExit=0, owner='WBS-X', costOwner='WBS-Y', formalUpdated=False,
                     newAcceptance=0, productTestsExecuted=0)
        self.assertEqual(1, verify(old, current, b, TASKS, {A, B}, {B: proof})['logicalCostSeparations'])
        for field, value in [('costOwner', 'WBS-X'), ('formalUpdated', True), ('newAcceptance', False),
                             ('productTestsExecuted', False)]:
            bad = dict(proof); bad[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                verify(old, current, b, TASKS, {A, B}, {B: bad})

    def test_runtime_transfer_flags_and_unrecorded_additions_are_rejected(self):
        for field, value in [('runtimeQualified', True), ('wholeAcceptance', True),
                             ('sourceBytesRecomputed', True), ('newAcceptance', False),
                             ('registeredAdditions', [])]:
            old, current, b = fixture(); b[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                verify(old, current, b, TASKS, {A, B}, {})


if __name__ == '__main__':
    unittest.main()
