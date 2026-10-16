"""New Main signing refuses historical3716, false quality and unregistered physical delta."""
import copy
import unittest
import pg3976_literal_invariant_signed_candidate as candidate
import pg3748_hygiene_signed_candidate_test as previous


class CurrentSignedCandidate(unittest.TestCase):
    def fixture(self):
        result = previous.Signed().fixture()
        gate = result['result']; gate.update(productionSource=candidate.SOURCE, tests=3717,
                                            newCases=[list(v) for v in candidate.whole.NEW_CASES],
                                            modules={m: dict(zip(['tests', 'suites', 'mainClasses'], v)) for m, v in candidate.whole.EXPECTED.items()})
        return result

    def test_exact_new_whole_delta_and_reject_old_or_false_quality(self):
        good = self.fixture(); gate = candidate.validate_gate(good, candidate.SOURCE)
        before = copy.deepcopy(gate['allPhysicalMainSha256']); before['api']['fixture/Class0.class'] = 'a' * 64
        try:
            candidate.GATE = gate; self.assertEqual(1643, candidate.verify_delta(before, gate['allPhysicalMainSha256']))
            wrong = copy.deepcopy(before); wrong['batch']['fixture/Class0.class'] = 'd' * 64
            with self.assertRaises(ValueError): candidate.verify_delta(wrong, gate['allPhysicalMainSha256'])
            for key, value in [('tests', 3716), ('productionSource', candidate.OLD_SOURCE), ('staticSixModules', 1), ('F03Accepted', True), ('formalAccepted', True), ('global100', True), ('oldNativeImported', True), ('changedClasses', []), ('newCases', [])]:
                bad = copy.deepcopy(good); bad['result'][key] = value
                with self.subTest(key=key), self.assertRaises(ValueError): candidate.validate_gate(bad, candidate.SOURCE)
        finally: candidate.GATE = None

    def test_new_only_host_template(self):
        raw = candidate.main_source(); compile(raw, '<host-only current3717>', 'exec')
        for value in ['PG3976', 'PG3748', '3717', '545', 'pg3968-literal-invariant-whole-qualified-v1', "len(gate['changedClasses'])", candidate.SOURCE]: self.assertIn(value, raw)
        for value in ['systemctl', 'daemon-reload', 'server.info', 'Root/noargs', 'PG3420', '3714']: self.assertNotIn(value, raw)


if __name__ == '__main__': unittest.main()
