import copy
import unittest

from wbs_broker_config_review_apply import CONFIG, eligible


class BrokerEligibility(unittest.TestCase):
    def fixture(self):
        task = {'id': 'WBS-C04', 'kind': 'CONFIG', 'ownedArtifacts': [CONFIG], 'sharedClassReferences': [],
                'dependencies': [], 'requirementIds': ['MQ-011', 'MQ-012', 'MQ-013']}
        row = {'id': 'WBS-C04'}
        proof = {'actualExit': 0, 'productionSource': 'same', 'ownedArtifact': CONFIG, 'formalUpdated': False,
                 'effortCompletionRate': None, 'runtimeBrokerStarted': False, 'newProductionPtCredit': 0,
                 'requirementIds': task['requirementIds'], 'artifactSha256': 'fixed',
                 'wholeActualOriginal': {'tests': 4, 'cases': [{'nonSuccessElements': []} for _ in range(4)],
                     'failures': 0, 'errors': 0, 'skipped': 0, 'brokerInputSha256': 'fixed', 'brokerActualSha256': 'fixed'},
                 'schemaCanary': {'compileExit': 0, 'actualExit': 0, 'originalAcceptedBeforeAndAfter': True, 'independentInvalidFourRejected': True},
                 'independentPolicy': {'globalFields': 24, 'addresses': 6, 'policyFieldsEach': 26, 'aclMatches': 13,
                                      'independentSemanticNegatives': 3, 'allRefused': True}}
        return task, row, proof

    def test_exact_non_java_scope_only(self):
        t, r, p = self.fixture(); eligible(t, r, p, 'same')
        for key, value in [('id', 'WBS-C05'), ('kind', 'COMPONENT'), ('ownedArtifacts', [CONFIG, 'src/Main.java']), ('dependencies', ['WBS-F03'])]:
            bad = copy.deepcopy(t); bad[key] = value
            with self.assertRaises(ValueError): eligible(bad, r, p, 'same')
        bad = dict(r, measuredFamilies=1)
        with self.assertRaises(ValueError): eligible(t, bad, p, 'same')

    def test_partial_or_inflated_proof_refused(self):
        t, r, p = self.fixture()
        for key, value in [('actualExit', 1), ('productionSource', 'other'), ('formalUpdated', True), ('runtimeBrokerStarted', True), ('newProductionPtCredit', 4)]:
            bad = copy.deepcopy(p); bad[key] = value
            with self.assertRaises(ValueError): eligible(t, r, bad, 'same')
        bad = copy.deepcopy(p); bad['wholeActualOriginal']['skipped'] = 1
        with self.assertRaises(ValueError): eligible(t, r, bad, 'same')
        bad = copy.deepcopy(p); bad['schemaCanary']['independentInvalidFourRejected'] = False
        with self.assertRaises(ValueError): eligible(t, r, bad, 'same')
        bad = copy.deepcopy(p); bad['independentPolicy']['allRefused'] = False
        with self.assertRaises(ValueError): eligible(t, r, bad, 'same')


if __name__ == '__main__':
    unittest.main()
