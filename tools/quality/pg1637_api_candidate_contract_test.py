"""Independent literal candidate gate and physical delta refusal vectors."""
import copy
import unittest
import pg1637_api_candidate_contract as p


class CandidateContractTest(unittest.TestCase):
    def gate(self):
        return {'actualExit': 0, 'result': {'actualExit': 0, 'productionSource': 'source', 'tests': 3596, 'suites': 532, 'mainClasses': 1643, 'FESFlakyNotRun': 0, 'staticSixModules': 0, 'classifierFourCounters100': True, 'global100': False, 'formalAccepted': False, 'jarHashes': {m: 'a' * 64 for m in p.MODULES}}}

    def test_exact_gate_and_each_wrong_missing_or_typed_boundary(self):
        self.assertEqual(3596, p.validate_gate(self.gate(), 'source')['tests'])
        for key, value in self.gate()['result'].items():
            for replacement in [None, True, 'wrong']:
                if type(value) is type(replacement) and value == replacement:
                    continue
                g = self.gate()
                g['result'][key] = replacement
                with self.subTest(key=key, replacement=replacement), self.assertRaises(ValueError):
                    p.validate_gate(g, 'source')
            g = self.gate()
            del g['result'][key]
            with self.subTest(missing=key), self.assertRaises(ValueError):
                p.validate_gate(g, 'source')
        for outer in [None, {}, {'actualExit': True}, {'actualExit': 1, 'result': self.gate()['result']}]:
            with self.assertRaises(ValueError):
                p.validate_gate(outer, 'source')

    def test_exact_three_changed_six_added_and_every_foreign_scope_refused(self):
        prefix = 'dev/codex/schubert/nk/api/bootstrap/'
        changed = [prefix + n + '.class' for n in ['ApiProcessMain', 'ApiProcessLifetime', 'ApiProcessLifetime$1']]
        added = [prefix + 'ApiTerminalCapture' + n + '.class' for n in ['', '$Factory', '$Open', '$Capture', '$Operation', '$Owner']]
        old = {m: {'Same.class': 'a' * 64} for m in p.MODULES}
        old['api'].update({n: 'a' * 64 for n in changed})
        new = copy.deepcopy(old)
        new['api'].update({n: 'b' * 64 for n in changed + added})
        self.assertEqual(15, p.verify_delta(old, new))
        for name in changed:
            bad = copy.deepcopy(new)
            bad['api'][name] = old['api'][name]
            with self.assertRaises(ValueError):
                p.verify_delta(old, bad)
        for name in added:
            bad = copy.deepcopy(new)
            del bad['api'][name]
            with self.assertRaises(ValueError):
                p.verify_delta(old, bad)
        for m in p.MODULES:
            bad = copy.deepcopy(new)
            bad[m]['Same.class'] = 'c' * 64
            with self.assertRaises(ValueError):
                p.verify_delta(old, bad)
            bad = copy.deepcopy(new)
            bad[m]['Foreign.class'] = 'c' * 64
            with self.assertRaises(ValueError):
                p.verify_delta(old, bad)


if __name__ == '__main__':
    unittest.main()
