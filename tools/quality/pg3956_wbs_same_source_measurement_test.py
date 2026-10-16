"""Measurement only, immutable acceptance/budget/artifacts and wrong-scope/counter refusal."""
import copy
import json
import unittest
import pg3956_wbs_same_source_measurement as current


class SameSourceMeasurement(unittest.TestCase):
    def test_measurement_without_new_acceptance_or_artifact_change(self):
        texts = {n: (current.PMO / n).read_text() for n in current.NAMES}
        proof = json.loads(current.PROOF.read_bytes()); result = current.candidates(texts, proof)
        self.assertEqual(texts[current.NAMES[0]], result[current.NAMES[0]])
        self.assertEqual(texts[current.NAMES[1]], result[current.NAMES[1]])
        inventory = json.loads(result[current.NAMES[2]]); old = json.loads(texts[current.NAMES[2]])
        self.assertEqual(old['artifacts'], inventory['artifacts'])
        snapshot = json.loads(result[current.NAMES[3]]); before = json.loads(texts[current.NAMES[3]])
        for a, b in zip(before['rows'], snapshot['rows'], strict=True):
            self.assertEqual(a['id'], b['id']); self.assertEqual(a.get('acceptance'), b.get('acceptance'))
        self.assertEqual({'LINE': 642, 'METHOD': 128, 'CLASS': 5, 'BRANCH': 459}, snapshot['sameSourceTechnicalMeasurementPG3956']['remaining'])
        self.assertEqual(0, snapshot['sameSourceTechnicalMeasurementPG3956']['acceptedLeafDelta'])
        self.assertIsNone(snapshot['wholeEffortCompletionRate'])

    def test_foreign_source_partial_cases_wrong_counters_and_gate_promotion_rejected(self):
        texts = {n: (current.PMO / n).read_text() for n in current.NAMES}
        original = json.loads(current.PROOF.read_bytes())
        for mode in ['source', 'cases', 'crc', 'counts', 'formal', 'f03']:
            proof = copy.deepcopy(original)
            if mode == 'source': proof['productionSource'] = 'a' * 40
            elif mode == 'cases': proof['allOriginal3714CasesRetained'] = False
            elif mode == 'crc': proof['all1643PhysicalMainUnchanged'] = False
            elif mode == 'counts': proof['remaining']['BRANCH'] = 0
            elif mode == 'formal': proof['formalAccepted'] = True
            else: proof['F03Accepted'] = True
            with self.subTest(mode=mode), self.assertRaises(ValueError): current.candidates(texts, proof)


if __name__ == '__main__':
    unittest.main()
