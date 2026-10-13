"""Actual composed handoff fixed identities; no live process mutation."""
import ast
import unittest
import pg2140_current_normal_pair_handoff as p


class HandoffTests(unittest.TestCase):
    def test_actual_pair_order_and_no_old_authority(self):
        raw=p.payload();tree=ast.parse(raw)
        calls=[n for n in ast.walk(tree)if isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id=='terminate']
        self.assertEqual([(ast.literal_eval(n.args[0]),ast.literal_eval(n.args[1]))for n in calls],[(676916,12181630),(676884,12181426)])
        values=[n.value for n in ast.walk(tree)if isinstance(n,ast.Constant)]
        for old in [291213,291242,291240,5962776,5962938]:self.assertNotIn(old,values)
        self.assertIn("['31']",raw);self.assertIn("['90']",raw)
        self.assertIn('pidfd_send_signal',raw);self.assertIn('candidateNotPlaced',raw)
        self.assertIn('replayAllowed',raw);self.assertIn('FRESH_READONLY_PROOF_COMPLETE',raw)
        self.assertNotIn('pg_terminate_backend',raw)
        self.assertFalse(any(isinstance(n,ast.Attribute)and n.attr=='SIGKILL'for n in ast.walk(tree)))
        self.assertNotIn('systemctl start',raw);self.assertNotIn('daemon-reload',raw)


if __name__=='__main__':unittest.main()
