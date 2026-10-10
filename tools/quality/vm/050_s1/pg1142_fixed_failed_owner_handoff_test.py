import ast
import unittest
from pg1142_fixed_failed_owner_handoff import payload


class HandoffTest(unittest.TestCase):
    def test_fixed_child_first_once_contract_scope_and_no_business_replay(self):
        text=payload();ast.parse(text)
        first=text.index('contract.terminate_once(404614,4248757')
        second=text.index('contract.terminate_once(404585,4248646')
        self.assertLess(first,second)
        for value in ['6119d517c5880b95815b03a32c35bc15627489aebb52fa26925195d9bcdcbc64',
                      'fixed-failed-owner-handoff-v1', 'os.pidfd_open(pid,0)', 'signal.pidfd_send_signal',
                      'contract.durable_reservation', 'after=post();require(after==post())',
                      "'oldOperationNormalClose':False", "'cleanupStillOriginalActiveExited':True"]:
            self.assertTrue(value in text, value)
        for value in ['systemctl stop','systemctl start','os.kill(','SIGKILL']:
            self.assertFalse(value in text, value)


if __name__=='__main__':unittest.main()
