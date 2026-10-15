import copy
import unittest
import pg3308_n13_saved_publication_proof as subject


class ExistingPublicationProofTest(unittest.TestCase):
    def test_actual_six_original_hash_payload_log_and_phase_distinction(self):
        records, hashes = subject.load_records()
        projected = subject.check_records(records)
        self.assertEqual(3, len(projected)); self.assertEqual(3, len(hashes))
        self.assertTrue(all(s['originalQualifiedSource'] != s['candidateSource'] for s in projected))

    def test_reject_false_source_scope_permission_unknown_and_early_activation(self):
        records, _ = subject.load_records()
        for stage, key, value in [('publication', 'newCurrentSource', subject.OLD), ('unused', 'candidateNotActivated', False), ('readonly', 'releaseReadonly', False), ('publication', 'coldPublicationSevenPhasesVerified', False), ('publication', 'permissionIssued', True), ('publication', 'parentBackendAdvisoryFlocksGone', False), ('publication', 'businessWrites', 1), ('publication', 'actualExit', None), ('publication', 'actualExit', False), ('unused', 'source', subject.SOURCE), ('readonly', 'boot', 'old-boot')]:
            bad = copy.deepcopy(records); bad[stage][1]['guest'][key] = value
            with self.subTest(stage=stage, key=key), self.assertRaises(ValueError):
                subject.check_records(bad)
        bad = copy.deepcopy(records); del bad['readonly']
        with self.assertRaises(ValueError):
            subject.check_records(bad)


if __name__ == '__main__':
    unittest.main()
