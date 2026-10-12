"""Actual fresh-preflight emitted source: retained failure and closed scope, no service changes."""
import ast
import unittest
from pg1849_warning_completed_current_before import payload,W
import json


class Before(unittest.TestCase):
    def test_actual_fullscope_persists_two_independent_seals_no_new_operations(self):
        raw=payload(json.loads((W/'pg1838-warning-terminal-independent-post-v1/manifest.safe.json').read_bytes()));ast.parse(raw)
        for value in ['pg1849-warning-completed-current-before-v1','before.private.json','native-before.private.json','allClientAdvisoryFlock0','managerFailureRetained=true','native == snapshot()']:
            self.assertIn(value,raw)
        for bad in ['StartUnit','StopUnit','ResetFailedUnit','pidfd_send_signal','pg_terminate_backend','genuineParentDone=true']:
            self.assertNotIn(bad,raw)


if __name__=='__main__':unittest.main()
