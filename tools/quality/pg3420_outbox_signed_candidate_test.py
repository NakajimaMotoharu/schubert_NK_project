import copy
import unittest

import pg3420_outbox_signed_candidate as candidate


class CandidateGateTest(unittest.TestCase):
    def gate(self):
        return {'actualExit': 0, 'result': {
            'actualExit': 0, 'productionSource': candidate.SOURCE, 'tests': 3712, 'suites': 545,
            'mainClasses': 1643, 'FESFlakyNotRun': 0, 'staticSixModules': 0,
            'semanticChangedClasses': 1, 'debugOnlyChangedClasses': 1,
            'oldNativeImported': False, 'candidateNativePending': True, 'formalAccepted': False,
            'global100': False, 'changedClasses': sorted(candidate.CHANGED),
            'allOriginalCaseIdentitiesRetained': True, 'newCases': [list(v) for v in candidate.whole.NEW_CASES],
            'generatedSwitchDebug': {'lineEntries': 1, 'oldLine': 154, 'newLine': 158, 'lineOffset': 4,
                                     'allNonLineBytesIdentical': True, 'crcEqualityClaim': False},
            'jarHashes': {m: 'a' * 64 for m in candidate.prior.MODULES},
            'modules': {m: dict(zip(['tests', 'suites', 'mainClasses'], values)) for m, values in candidate.whole.EXPECTED.items()}}}

    def test_requires_actual_new_whole_and_never_old_native_or_formal(self):
        good = self.gate(); self.assertEqual(good['result'], candidate.validate_gate(good, candidate.SOURCE))
        for key, bad in [('productionSource', candidate.OLD_SOURCE), ('tests', 3707), ('suites', 543),
                         ('mainClasses', 1642), ('staticSixModules', 1), ('FESFlakyNotRun', 1),
                         ('oldNativeImported', True), ('formalAccepted', True), ('changedClasses', [])]:
            wrong = copy.deepcopy(good); wrong['result'][key] = bad
            with self.subTest(key=key), self.assertRaises(ValueError):
                candidate.validate_gate(wrong, candidate.SOURCE)
        for wrong in [None, {}, {'actualExit': False}, {'actualExit': 1}]:
            with self.assertRaises(ValueError): candidate.validate_gate(wrong, candidate.SOURCE)

    def test_all_physical_classes_and_pure_no_lifecycle_sign_template(self):
        before = {m: {} for m in candidate.prior.MODULES}
        before['api'] = {n.split(':', 1)[1]: 'a' * 64 for n in candidate.CHANGED}
        before['batch'] = {str(i) + '.class': 'a' * 64 for i in range(1641)}
        after = copy.deepcopy(before)
        for key in after['api']: after['api'][key] = 'b' * 64
        self.assertEqual(1643, candidate.verify_delta(before, after))
        wrong = copy.deepcopy(after); wrong['batch']['0.class'] = 'b' * 64
        with self.assertRaises(ValueError): candidate.verify_delta(before, wrong)
        raw = candidate.main_source(); compile(raw, '<pure host sign template>', 'exec')
        for marker in ['PG3420', 'PG2802', '3712', '545', 'qualification_matches(outer)']:
            self.assertIn(marker, raw)
        for forbidden in ['systemctl', 'daemon-reload', 'Root/noargs', 'server.info']:
            self.assertNotIn(forbidden, raw)


if __name__ == '__main__':
    unittest.main()
