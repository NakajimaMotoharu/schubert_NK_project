"""Actual completion data does not certify parent PID1 success; all whole gates."""
import ast
import unittest
from pg1838_warning_terminal_independent_post import payload,SEALS,SLOT


class Post(unittest.TestCase):
    def test_actual_current_complete_bytes_uuid_and_full_resource_gates(self):
        raw=payload({k:'a'*64 for k in SEALS});tree=ast.parse(raw);values=[n.value for n in ast.walk(tree)if isinstance(n,ast.Constant)]
        self.assertTrue(any(type(v)is bytes and v.startswith(b'genuineParentWarningOriginal=true\nmanagerFailureRetained=true\n')for v in values))
        self.assertFalse(any(type(v)is bytes and v.startswith(b'genuineParentDone=true')for v in values))
        self.assertTrue('9adbf05a-61d0-408b-b51d-ab19c7e5b16a'in raw)
        self.assertTrue(SLOT in raw);self.assertTrue('pg1833-warning-owned-stop-tools-v1'in raw)
        self.assertTrue('allTenUnitsKernelEmpty'in raw);self.assertTrue('allClientAdvisoryFlock0'in raw)
        self.assertFalse('systemctl stop'in raw);self.assertFalse('pidfd_send_signal'in raw)


if __name__=='__main__':unittest.main()
