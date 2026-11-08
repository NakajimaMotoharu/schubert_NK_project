"""Pure metadata regressions. No Product, runtime collector, VM, real DB or old evidence access."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import wbs_current_source_structure as target


SOURCE = 'a' * 40
PATH_A = 'src/example/src/main/java/example/One.java'
PATH_B = 'src/deployment/monitoring/one.template'
PATH_C = 'program/characterization/src/main/java/example/Adapter.java'
RETIRED = 'src/example/src/main/java/example/Retired.java'


def fixture():
    base = [dict(path=p, staticSource=SOURCE, sha256=str(n) * 64, kind='JAVA' if p.endswith('.java') else 'DEPLOYMENT',
                 owner='WBS-A', costOwner='WBS-A', qualification='UNQUALIFIED_STATIC_DESCRIPTOR_ONLY',
                 runtimeQualificationTransferred=False, acceptance='UNASSESSED')
            for n, p in enumerate([PATH_A, PATH_B, PATH_C], 1)]
    legacy = [dict(path=PATH_A, owner='WBS-B', costOwner='WBS-B', kind='JAVA'),
              dict(path=RETIRED, owner='WBS-A', costOwner='WBS-A', kind='JAVA')]
    tasks = [dict(id='WBS-A', executionRole='WORK'), dict(id='WBS-B', executionRole='WORK')]
    view = dict(version=1, source=SOURCE, runtimeQualified=False, wholeAcceptance=False,
                oldRuntimeQualificationTransferred=False, artifactCount=3,
                ownerKindOverrides={PATH_A: dict(owner='WBS-B', costOwner='WBS-B', kind='JAVA')},
                addedComparedToLegacy=[PATH_C, PATH_B], retiredHistoricalPaths=[RETIRED],
                productionArtifacts=2, characterizationArtifacts=1)
    view['addedComparedToLegacy'].sort()
    return view, base, legacy, tasks, {PATH_A, PATH_B, PATH_C}


class StructureTest(unittest.TestCase):
    def test_valid_static_owner_override_keeps_identity_and_history(self):
        values = fixture()
        before = copy.deepcopy(values)
        result = target.resolve_descriptors(*values)
        self.assertEqual('WBS-B', result[0]['owner'])
        self.assertEqual('1' * 64, result[0]['sha256'])
        self.assertEqual(before, values)
        self.assertFalse(result[0]['runtimeQualificationTransferred'])

    def test_source_and_runtime_mutations_fail_closed(self):
        mutations = [
            lambda v, b, l, t, n: b[0].update(staticSource='b' * 40),
            lambda v, b, l, t, n: b[0].update(runtimeQualificationTransferred=True),
            lambda v, b, l, t, n: b[0].update(acceptance='ACCEPTED'),
            lambda v, b, l, t, n: b[0].update(qualification='CURRENT_RUNTIME_QUALIFIED'),
            lambda v, b, l, t, n: v.update(runtimeQualified=True),
            lambda v, b, l, t, n: v.update(wholeAcceptance=True),
            lambda v, b, l, t, n: v.update(oldRuntimeQualificationTransferred=True),
        ]
        for mutate in mutations:
            with self.subTest(mutation=mutate):
                values = fixture()
                mutate(*values)
                with self.assertRaises(ValueError):
                    target.resolve_descriptors(*values)

    def test_missing_duplicate_path_and_retired_mismatch_are_not_accepted(self):
        for mutate in [lambda v, b, l, t, n: b.append(copy.deepcopy(b[0])),
                       lambda v, b, l, t, n: n.remove(PATH_B),
                       lambda v, b, l, t, n: v.update(addedComparedToLegacy=[]),
                       lambda v, b, l, t, n: v.update(retiredHistoricalPaths=[]),
                       lambda v, b, l, t, n: v.update(productionArtifacts=3)]:
            values = fixture()
            mutate(*values)
            with self.assertRaises(ValueError):
                target.resolve_descriptors(*values)

    def test_identity_owner_kind_and_alias_boundaries(self):
        mutations = [
            lambda v, b, l, t, n: v['ownerKindOverrides'][PATH_A].update(sha256='0' * 64),
            lambda v, b, l, t, n: v['ownerKindOverrides'][PATH_A].update(owner='UNKNOWN'),
            lambda v, b, l, t, n: v['ownerKindOverrides'][PATH_A].update(costOwner='WBS-A'),
            lambda v, b, l, t, n: v['ownerKindOverrides'][PATH_A].update(kind='RESOURCE'),
            lambda v, b, l, t, n: t[1].update(executionRole='REFERENCE_ONLY'),
            lambda v, b, l, t, n: v['ownerKindOverrides'].update({'not-present': dict(owner='WBS-A', costOwner='WBS-A', kind='JAVA')}),
        ]
        for mutate in mutations:
            values = fixture()
            mutate(*values)
            with self.assertRaises(ValueError):
                target.resolve_descriptors(*values)

    def test_test_filenames_are_excluded_without_reading_or_hashing(self):
        paths = [PATH_A, PATH_B, PATH_C,
                 'src/example/src/test/java/RootFailedStartRecoveryTest.java',
                 'src/example/src/test/java/RootFailedStartPairRecoveryTest.java']
        self.assertEqual({PATH_A, PATH_B, PATH_C}, target.eligible_names(paths))

    def test_noncanonical_metadata_paths_and_duplicate_keys(self):
        for value in ['/private/credential.json', '../secret.json', 'a/../b', 'a\\b', 'a\0b', 'a//b']:
            with self.assertRaises(ValueError):
                target.safe_relative(value)
        with self.assertRaises(ValueError):
            target.unique_object([('source', 'a'), ('source', 'b')])

    def test_full_audit_cannot_convert_structure_pass_into_runtime_acceptance(self):
        structure = dict(status='PASS_CURRENT_STATIC_SOURCE_STRUCTURE_ONLY', source=SOURCE,
                         runtimeQualified=False, wholeWbsAccepted=False)
        legacy = dict(source='b' * 40, currentPhysicalCandidate=dict(source='c' * 40))
        report = target.full_audit_hold(structure, legacy)
        self.assertEqual('HOLD', report['status'])
        self.assertFalse(report['privateRuntimeEvidenceRead'])
        self.assertFalse(report['wholeWbsAccepted'])
        self.assertEqual(0, report['newAcceptance'])
        self.assertTrue(report['unverifiedChecks'])
        for field in ['runtimeQualified', 'wholeWbsAccepted']:
            bad = dict(structure)
            bad[field] = True
            with self.assertRaises(ValueError):
                target.full_audit_hold(bad, legacy)

    def test_complete_public_binding_reads_metadata_only(self):
        view, base, legacy, tasks, names = fixture()
        with tempfile.TemporaryDirectory(prefix='wbs-static-metadata-') as tmp:
            root = Path(tmp)
            prefix = root / target.PUBLIC_PREFIX / 'OWN-METADATA'
            prefix.mkdir(parents=True)

            def put(name, value):
                p = prefix / name
                p.write_text(json.dumps(value))
                return dict(path=p.relative_to(root).as_posix(), sha256=hashlib.sha256(p.read_bytes()).hexdigest())

            base_ref = put('artifacts.json', base)
            lineage = dict(actualExit=0, source=SOURCE, artifactCount=3, files={'artifacts.json': base_ref['sha256']})
            lineage_ref = put('lineage.json', lineage)
            identity_ref = put('identity.json', dict(actualExit=0, productionMainSource=SOURCE,
                                                    currentLineage=lineage_ref, artifacts=3,
                                                    whole451Accepted=False, wholeG13Accepted=False))
            view.update(identityProof=identity_ref, lineageManifest=lineage_ref, descriptorBase=base_ref,
                        preservedLegacyInventorySource='b' * 40, preservedLegacyCandidateSource='c' * 40)
            inventory = dict(source='b' * 40, currentPhysicalCandidate=dict(source='c' * 40), artifacts=legacy,
                             **{target.VIEW_KEY: view})
            view.update(preservedLegacyArtifactRowsDigest=target.value_digest(legacy),
                        preservedLegacyCandidateDigest=target.value_digest(inventory['currentPhysicalCandidate']))
            ip = root / 'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json'
            ip.parent.mkdir(parents=True)
            ip.write_text(json.dumps(inventory))
            snapshot = dict(source='b' * 40, inventorySha256=target.digest(ip))
            master = dict(tasks=tasks, **{target.PROJECTION_KEY: dict(source=SOURCE, viewKey=target.VIEW_KEY,
                         artifactCount=3, ownerArtifactCounts={'WBS-B': 1, 'WBS-A': 2},
                         runtimeQualified=False, newAcceptance=0, effortRate=None, descriptorBase=base_ref)})
            with patch.object(target.subprocess, 'run', side_effect=AssertionError('no Git/runtime subprocess for supplied names')):
                result = target.verify(root, master, snapshot, inventory, git_names=names)
            self.assertEqual(3, result['artifactCount'])
            self.assertFalse(result['identityRecomputed'])
            self.assertFalse(result['runtimeQualified'])
            for field, invalid in [('runtimeQualified', True), ('newAcceptance', 1),
                                   ('newAcceptance', False), ('effortRate', 0.5),
                                   ('descriptorBase', dict(path='unbound.json', sha256='0' * 64))]:
                bad = copy.deepcopy(master)
                bad[target.PROJECTION_KEY][field] = invalid
                with self.subTest(projectionField=field, invalid=invalid), self.assertRaises(ValueError):
                    target.verify(root, bad, snapshot, inventory, git_names=names)
            # A forged proof is rejected by its original pin before it could qualify a source.
            (prefix / 'identity.json').write_text('{}')
            with self.assertRaises(ValueError):
                target.verify(root, master, snapshot, inventory, git_names=names)


if __name__ == '__main__':
    unittest.main()
