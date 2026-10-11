import ast
import unittest
from pg1464_failed_current_capture import payload


class FailedCaptureTest(unittest.TestCase):
    def test_failure_not_success_or_authority(self):
        s=payload();compile(s,'<failed current capture>','exec')
        self.assertIn("m['Result']=='timeout'",s)
        self.assertIn("m['ExecMainStatus']=='143'",s)
        self.assertIn("'newDoneAbsent':True",s)
        self.assertIn("'stopRevokeRetirementIssued':False",s)
        self.assertIn('67108864',s)
        calls=[ast.unparse(n.func)for n in ast.walk(ast.parse(s))if isinstance(n,ast.Call)]
        for value in ['manager.StartUnit','manager.StopUnit','signal.pidfd_send_signal','os.kill']:self.assertNotIn(value,calls)


if __name__=='__main__':unittest.main()
