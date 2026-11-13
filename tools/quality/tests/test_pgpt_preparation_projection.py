"""Independent tiny relocation/registration fixtures; never inspect production class binaries."""
import copy
import unittest
from wbs_current_source_structure import preparation_projection, value_digest


class PreparationProjectionTest(unittest.TestCase):
    def setUp(self):
        self.old = 'src/old/src/main/java/Old.java'
        self.new = 'src/new/src/main/java/New.java'
        self.extra = 'src/new/src/main/java/Extra.java'
        self.legacy = [dict(path=self.old, owner='WBS-A', costOwner='WBS-A', kind='JAVA')]
        self.current = copy.deepcopy(self.legacy)
        self.base = [dict(path=self.new, owner='WBS-A', costOwner='WBS-A', kind='JAVA',
                          sha256='b' * 64, staticSource='a' * 40,
                          qualification='UNQUALIFIED_STATIC_DESCRIPTOR_ONLY',
                          runtimeQualificationTransferred=False, acceptance='UNASSESSED')]
        self.tasks = [dict(id='WBS-A', executionRole='WORK'), dict(id='WBS-B', executionRole='WORK')]
        self.view = dict(source='a' * 40, version=1, artifactCount=1, productionArtifacts=1,
                         characterizationArtifacts=0, ownerKindOverrides={},
                         runtimeQualified=False, wholeAcceptance=False,
                         oldRuntimeQualificationTransferred=False,
                         addedComparedToLegacy=[self.new], retiredHistoricalPaths=[self.old],
                         preservedLegacyArtifactRowsDigest=value_digest(self.legacy))

    def project(self, additions=None):
        return preparation_projection(self.view, self.base, self.legacy, self.current,
                                      self.tasks, [self.new], 'WBS-A', additions or [])

    def test_relocated_source_replaces_old_path_without_runtime_or_byte_transfer(self):
        result = self.project()
        self.assertEqual([self.new], result['paths'])
        self.assertFalse(result['runtimeQualified'])
        self.assertFalse(result['baselineByteQualificationTransferred'])

    def test_frozen_legacy_digest_is_required(self):
        self.view['preservedLegacyArtifactRowsDigest'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'frozen legacy'):
            self.project()

    def test_unlisted_registration_is_rejected(self):
        self.current.append(dict(path=self.extra, owner='WBS-A', costOwner='WBS-A',
                                 kind='JAVA', acceptance='UNASSESSED'))
        with self.assertRaisesRegex(ValueError, 'unlisted'):
            self.project()

    def test_explicit_unqualified_addition_is_included_once(self):
        self.current.append(dict(path=self.extra, owner='WBS-A', costOwner='WBS-A',
                                 kind='JAVA', acceptance='UNASSESSED'))
        self.assertEqual([self.extra, self.new], self.project([self.extra])['paths'])

    def test_other_owner_addition_does_not_enter_this_scope(self):
        self.current.append(dict(path=self.extra, owner='WBS-B', costOwner='WBS-B',
                                 kind='JAVA', acceptance='UNASSESSED'))
        self.assertEqual([self.new], self.project([self.extra])['paths'])

    def test_owner_changes_are_not_hidden_by_relocation(self):
        self.current[0]['owner'] = 'WBS-B'
        with self.assertRaisesRegex(ValueError, 'ownership changed'):
            self.project()

    def test_duplicate_current_registration_is_rejected(self):
        self.current.append(copy.deepcopy(self.current[0]))
        with self.assertRaisesRegex(ValueError, 'duplicate current'):
            self.project()

    def test_wrong_retirement_catalog_is_rejected_by_original_resolver(self):
        self.view['retiredHistoricalPaths'] = []
        with self.assertRaisesRegex(ValueError, 'retired artifact'):
            self.project()

    def test_runtime_qualified_view_cannot_mint_preparation_authority(self):
        self.view['runtimeQualified'] = True
        with self.assertRaisesRegex(ValueError, 'runtime transfer'):
            self.project()

    def test_historical_data_and_view_are_not_mutated(self):
        before = copy.deepcopy((self.view, self.base, self.legacy, self.current, self.tasks))
        self.project()
        self.assertEqual(before, (self.view, self.base, self.legacy, self.current, self.tasks))

    def test_existing_not_run_registration_remains_unqualified(self):
        self.current.append(dict(path=self.extra, owner='WBS-A', costOwner='WBS-A',
                                 kind='JAVA', acceptance='NOT_RUN'))
        result = self.project([self.extra])
        self.assertEqual([self.extra, self.new], result['paths'])
        self.assertFalse(result['wholeAcceptance'])

    def test_accepted_registration_cannot_import_acceptance(self):
        self.current.append(dict(path=self.extra, owner='WBS-A', costOwner='WBS-A',
                                 kind='JAVA', acceptance='ACCEPTED'))
        with self.assertRaisesRegex(ValueError, 'unqualified public'):
            self.project([self.extra])


if __name__ == '__main__':
    unittest.main()
