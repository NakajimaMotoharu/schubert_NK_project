import ast
import unittest
import pg4086_failed_done_recovery_contract as recovery


class RecoveryContractTest(unittest.TestCase):
    def test_only_actual_reverse_six_and_single_use(self):
        self.assertEqual(('caddy.service','schubert-nk-web.service','schubert-nk-api.service',
                          'schubert-nk-expiry-cleanup.service','artemis.service','schubert-nk-cleanup.service'), recovery.ORDER)
        p = recovery.Plan()
        for unit in recovery.ORDER:
            p.reserve(unit)
            with self.assertRaises(ValueError): p.reserve(unit)
            p.terminal(unit)
            with self.assertRaises(ValueError): p.terminal(unit)
        p.revoke(); p.finish()
        with self.assertRaises(ValueError): p.finish()
        with self.assertRaises(ValueError): p.revoke()

    def test_no_early_revoke_finish_skip_extra_or_unknown(self):
        for at in range(6):
            p = recovery.Plan()
            for unit in recovery.ORDER[:at]: p.reserve(unit); p.terminal(unit)
            with self.assertRaises(ValueError): p.revoke()
            with self.assertRaises(ValueError): p.finish()
            for forbidden in [None, 'schubert-nk-morning-controller.service', 'schubert-nk-backup.service',
                              'schubert-nk-inbox-inspector.service', recovery.ORDER[(at + 1) % 6]]:
                with self.assertRaises(ValueError): p.reserve(forbidden)

    def test_independent_epoch_exact_delta_preserves_binding(self):
        old = (b'NKEPOCH1\nstate=ISSUED\nboot_id=79a3260a-e16d-42bf-942a-b914ed144c28\n'
               b'epoch_id=11111111-2222-4333-8444-555555555555\nrun_id=dc0cb75f-1dbd-4b64-bb1c-b4d91e592c4f\n'
               b'cutoff_utc=2026-10-16T05:44:47.267413Z\nactivation_id=d9d58371-bf80-49f6-bad9-3d1e0916fb04\n'
               b'permit_sha256=0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef\n')
        expected = (b'NKEPOCH1\nstate=INVALID\nboot_id=79a3260a-e16d-42bf-942a-b914ed144c28\n'
               b'epoch_id=11111111-2222-4333-8444-555555555555\nrun_id=dc0cb75f-1dbd-4b64-bb1c-b4d91e592c4f\n'
               b'cutoff_utc=2026-10-16T05:44:47.267413Z\nactivation_id=d9d58371-bf80-49f6-bad9-3d1e0916fb04\npermit_sha256=-\n')
        self.assertEqual(expected, recovery.invalid_epoch(old))
        for value in [None, b'', old + b'\n', expected,
                      old.replace(b'11111111-2222-4333-8444-555555555555', b'00000000-0000-0000-0000-000000000000'),
                      old.replace(b'cutoff_utc=', b'cutoff='),old.replace(b'cutoff_utc=', b'unknown='),
                      old.replace(b'\n',b'\r\n'),old.replace(b'cutoff_utc=',b'activation_id='),
                      old.replace(b'dc0cb75f-1dbd-4b64-bb1c-b4d91e592c4f',b'11111111-2222-4333-8444-555555555555'),
                      old.replace(b'0123456789abcdef', b'0123456789abcdeg')]:
            with self.assertRaises(ValueError): recovery.invalid_epoch(value)

    def test_shared_terminal_mechanics_not_parent_success_or_dispatch(self):
        values = recovery.shared_sources(); common = values['recovery_terminal.py']
        ns = {n.name for n in ast.parse(common).body if isinstance(n, ast.FunctionDef)}
        self.assertEqual({'require','kernel_empty','terminal','same_generation','normal_terminal','broker_witness'}, ns)
        self.assertFalse('genuineRootDone' in common or 'parent_receipt' in common or 'subprocess' in common)
        self.assertEqual(3, len(values))


if __name__ == '__main__': unittest.main()
