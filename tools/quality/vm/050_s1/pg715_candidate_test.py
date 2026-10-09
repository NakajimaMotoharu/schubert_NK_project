"""Literal closed byte delta and exhaustive one-field perturbations; no signing."""
import ast
import copy
import unittest
from pg715_candidate_contract import MODULES, CHANGED, ADDED, verify_delta
from pg715_candidate_build import source


class Test(unittest.TestCase):
    def fixture(self):
        old = {m: {'public/' + m + '.class': '0'*64} for m in MODULES}
        old['batch']['dev/codex/schubert/nk/batch/file/CleanupExpiryExecution.class'] = '0'*64
        new = copy.deepcopy(old)
        for name in CHANGED['batch']: new['batch'][name] = '1'*64
        for name in ADDED['batch']: new['batch'][name] = '2'*64
        return old, new

    def test_closed_delta_and_each_module_change_add_remove_or_bad_digest(self):
        old, new = self.fixture(); self.assertEqual(verify_delta(old, new), 9)
        for module in MODULES:
            for mode in ('changed', 'extra', 'removed', 'digest'):
                candidate = copy.deepcopy(new); name = 'public/' + module + '.class'
                if mode == 'changed': candidate[module][name] = '9'*64
                elif mode == 'extra': candidate[module]['public/unexpected.class'] = '3'*64
                elif mode == 'removed': del candidate[module][name]
                else: candidate[module][name] = 'UNKNOWN'
                with self.subTest(module=module, mode=mode), self.assertRaises(ValueError): verify_delta(old, candidate)
        for bad in (None, {}, {'batch': None}):
            with self.assertRaises(ValueError): verify_delta(old, bad)
        for name in ADDED['batch']:
            candidate = copy.deepcopy(new); del candidate['batch'][name]
            with self.assertRaises(ValueError): verify_delta(old, candidate)

    def test_real_frozen_gate_and_current_baseline_before_signature(self):
        raw = source(); ast.parse(raw)
        for value in ('pg713-expiry-six-host-v1', 'pg715-release-v1', 'pg682-release-v1',
                      '1ec19782a1afe22d1de75b05f4cd12b8a8a8a172', '3502', '517', '1614',
                      '5f6a57015fb30d8f2097e594370d558ac6202a9d5d2ed98ce0108494cc7f524a',
                      '076fbb16c96eecc0357cbc41b4c081c9cb9d652ea6da94d67625ac7623e5d480'):
            self.assertIn(value, raw)
        self.assertLess(raw.index('verify_delta(old_classes, new_classes)'), raw.index("'-sign'"))
        self.assertNotIn('pg631-release-v1', raw)
        self.assertIn("{'VERSION', 'operations/batch.jar'} <= changed", raw)


if __name__ == '__main__': unittest.main()
