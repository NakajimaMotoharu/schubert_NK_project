import ast
import unittest
from pg1035_cold_owned_handoff import payload


class Handoff(unittest.TestCase):
    def test_only_fixed_old_actor_once_with_scope_retention_before_cleanup(self):
        raw = payload()
        tree = ast.parse(raw)
        self.assertIn('contract.terminate_once(3091, 835207', raw)
        self.assertIn("contract.durable_reservation(reservation_fd, '3091.term-reserved.private.json'", raw)
        self.assertIn('if RESERVATION_ATTEMPTED:\n        retain(failure)', raw)
        self.assertIn('OWNER_PID = 0', raw)
        self.assertIn('contract.free_flocks(lines, m)', raw)
        self.assertIn('require(value == prior_value)', raw)
        self.assertIn("expected = {k: v for k, v in before.items() if k != 'actor'}", raw)
        sends = [n for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == 'pidfd_send_signal']
        self.assertEqual(1, len(sends))
        self.assertFalse(any(isinstance(n, ast.Attribute) and n.attr == 'SIGKILL' for n in ast.walk(tree)))
        receipt = tree.body[-1].value.args[0].args[0]
        self.assertIsInstance(receipt, ast.Dict)
        values = {key.value: value for key, value in zip(receipt.keys, receipt.values)}
        self.assertNotIn('oldActorUntouched', values)
        self.assertIsNone(values['oldTransportExit'].value)
        self.assertIs(False, values['oldOperationNormalClose'].value)


if __name__ == '__main__': unittest.main()
