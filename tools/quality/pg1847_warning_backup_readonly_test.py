"""Current Root13 Backup literal identity and full scope/readonly capabilities."""
import ast
import unittest
from pg1847_warning_backup_readonly import payload


class Backup(unittest.TestCase):
    def test_actual_current_role_binding_and_no_backup_restore_or_start(self):
        raw=payload();ast.parse(raw)
        for literal in ['4148e3e8-f107-431a-ab27-d6e6d1f1772e','2026-10-12T18:20:32.598894Z','pg1833_parent_receipt.py','pg1847-warning-backup-readonly-v1','pg1833-native-stop-v1','managerFailureRetained=true']:
            self.assertIn(literal,raw)
        for old in ['0be226b1-bbb7-43d3-aa9e-59d0bda70f9a','pg1609_parent_receipt.py','genuineParentDone=true','StartUnit','StopUnit','-d schubert']:
            self.assertNotIn(old,raw)


if __name__=='__main__':unittest.main()
