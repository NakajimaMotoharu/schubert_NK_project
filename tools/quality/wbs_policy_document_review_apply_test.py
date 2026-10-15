import copy
import unittest

from wbs_policy_document_review_apply import document_eligible


class PolicyEligibility(unittest.TestCase):
    def fixture(self):
        return ({'id': 'WBS-F01', 'kind': 'FOUNDATION', 'ownedArtifacts': [], 'requirementIds': []},
                {'id': 'WBS-F01', 'measurementStatus': 'ARTIFACT_CONFIRMED'},
                {'productionSource': 'fixed', 'actualExit': 0, 'coverageApplicability': 'NON_EXECUTABLE_POLICY_DOCUMENT',
                 'javaCoverageExcluded': False, 'F03Accepted': False, 'formalUpdated': False,
                 'wholeEffortCompletionRate': None, 'policySections': [str(i) for i in range(1, 15)],
                 'productionModules': ['protocol', 'storage', 'bootstrap', 'api', 'web', 'batch'],
                 'separateCompatibilityModule': 'program/characterization', 'allSevenPomHashesEqualA9': True})

    def test_policy_accepted_but_never_uses_java_counter_shortcut(self):
        t, r, p = self.fixture(); document_eligible(t, r, p, 'fixed')
        for key, value in [('ownedArtifacts', ['src/a.java']), ('kind', 'COMPONENT'), ('id', 'WBS-F03')]:
            bad = copy.deepcopy(t); bad[key] = value
            with self.assertRaises(ValueError):document_eligible(bad, r, p, 'fixed')

    def test_partial_or_inflated_policy_proofs_refused(self):
        t, r, p = self.fixture()
        for key, value in [('actualExit', 1), ('F03Accepted', True), ('javaCoverageExcluded', True),
                           ('formalUpdated', True), ('policySections', ['1']), ('productionModules', ['protocol'])]:
            bad = copy.deepcopy(p); bad[key] = value
            with self.assertRaises(ValueError):document_eligible(t, r, bad, 'fixed')


if __name__ == '__main__':unittest.main()
