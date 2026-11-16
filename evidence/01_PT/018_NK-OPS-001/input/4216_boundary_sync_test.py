"""Eight independent metadata contracts, no access to actual checkpoints or production processes."""
from copy import deepcopy
import unittest
from pmo_manufacturing_boundary import synchronize_boundary

CORE = '4' * 40
EVENT = 'PGPT-UNIT-END1'


class BoundarySyncTest(unittest.TestCase):
    def setUp(self):
        self.document = dict(
            currentManufacturingBoundary=dict(productionCoreMain=CORE, stage='PT_NOT_RUN', knownOwnActiveJobs=['HISTORICAL_ONLY']),
            actualForeignField='KEEP', pgptAllComplete=False,
        )
        self.config = dict(category='IMPLEMENTATION', sourceAfter=CORE, manifestPath='evidence/example/manifest.json', manifestSha256='b' * 64, outcome='PARTIAL_SCOPE_ONLY', terminalAtUTC='2026-11-16T00:00:00Z')
        self.manifest = dict(actualExit=0, productionCoreMain=CORE, actualUnitSource='a' * 40, whole451Accepted=False)

    def call(self, document=None, config=None, manifest=None, event=EVENT, mode='end'):
        return synchronize_boundary(self.document if document is None else document, self.config if config is None else config, self.manifest if manifest is None else manifest, event, mode)

    def test_verified_end_preserves_original_boundary_and_unrelated_fields(self):
        before = deepcopy(self.document)
        result = self.call()
        self.assertEqual('ACTIVITY_ENDED_SCOPE_ONLY', result['currentManufacturingBoundary']['stage'])
        self.assertEqual(EVENT, result['currentManufacturingBoundary']['completedEvent'])
        self.assertEqual([before['currentManufacturingBoundary']], result['manufacturingBoundaryHistory'])
        self.assertEqual('KEEP', result['actualForeignField'])
        self.assertEqual(before, self.document)
        result['manufacturingBoundaryHistory'][0]['knownOwnActiveJobs'].append('LOCAL_MUTATION')
        self.assertEqual(['HISTORICAL_ONLY'], self.document['currentManufacturingBoundary']['knownOwnActiveJobs'])

    def test_start_and_nonproduct_categories_are_unchanged(self):
        self.assertEqual(self.document, self.call(mode='start'))
        for category in ['ADMIN', 'REVIEW', 'CONTRACT_AUDIT', 'RECOVERY']:
            self.assertEqual(self.document, self.call(config=dict(self.config, category=category)))

    def test_absent_or_nonobject_manual_boundary_is_not_created(self):
        for value in [dict(actualForeignField='KEEP'), dict(currentManufacturingBoundary=None), dict(currentManufacturingBoundary='HISTORY')]:
            self.assertEqual(value, self.call(document=value))

    def test_foreign_core_is_never_overwritten(self):
        foreign = dict(self.document, currentManufacturingBoundary=dict(productionCoreMain='5' * 40, stage='UNKNOWN'))
        self.assertEqual(foreign, self.call(document=foreign))

    def test_bad_core_manifest_or_unsuccessful_activity_is_rejected(self):
        for config, manifest in [(dict(self.config, sourceAfter='bad'), self.manifest), (self.config, dict(self.manifest, productionCoreMain='5' * 40)), (self.config, dict(self.manifest, actualExit=1)), (self.config, dict(self.manifest, actualExit=False))]:
            with self.assertRaises(ValueError):
                self.call(config=config, manifest=manifest)
        self.assertNotIn('manufacturingBoundaryHistory', self.document)

    def test_same_event_is_idempotent(self):
        first = self.call()
        second = self.call(document=first)
        self.assertEqual(first, second)
        self.assertEqual(1, len(second['manufacturingBoundaryHistory']))

    def test_scope_end_does_not_promote_quality_or_ownership(self):
        result = self.call()['currentManufacturingBoundary']
        self.assertEqual('PARTIAL_SCOPE_ONLY', result['scopeOutcome'])
        self.assertFalse(result['whole451Accepted'])
        self.assertFalse(result['formalUpdated'])
        self.assertEqual(0, result['newAcceptance'])
        self.assertIsNone(result['effortRate'])
        self.assertEqual('NOT_INFERRED_FROM_ACTIVITY_END', result['ownProcessAndVmState'])
        self.assertNotIn('knownOwnActiveJobs', result)
        self.assertTrue(result['scopeEvidenceOnly'])

    def test_bad_evidence_event_or_history_is_rejected_without_mutating_input(self):
        for config in [dict(self.config, manifestPath='private/raw'), dict(self.config, manifestPath='evidence/../raw'), dict(self.config, manifestSha256='invalid')]:
            with self.assertRaises(ValueError):
                self.call(config=config)
        with self.assertRaises(ValueError):
            self.call(event='')
        wrong = dict(self.document, manufacturingBoundaryHistory='PRESERVE')
        with self.assertRaises(ValueError):
            self.call(document=wrong)
        self.assertEqual('PRESERVE', wrong['manufacturingBoundaryHistory'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
