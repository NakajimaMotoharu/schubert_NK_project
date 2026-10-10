import ast
import unittest
from pg1193_completed_resume_receipt import GC, BINDING, qualify_current, payload
from pg1185_current_resume_receipt_test import ResumeReceiptTest


class CompletedReceiptTest(unittest.TestCase):
    def test_gc_is_not_completion_and_retained_state_independent(self):
        self.assertEqual(qualify_current(dict(GC)),'GC_CURRENT_NOT_COMPLETION_PROOF')
        state=dict(GC,InvocationID='a14cc600a4fd4f2e9d8c4731ad9d754b',ExecMainCode='1',ExecMainStartTimestampMonotonic='51172132518',ExecMainExitTimestampMonotonic='52530445203')
        self.assertEqual(qualify_current(state),'RETAINED_CURRENT_SEPARATE_FROM_PID1')

    def test_null_unknown_live_partial_gc_foreign_or_timeout_rejected(self):
        for bad in [None,{},[],dict(GC,extra=0)]:
            with self.assertRaises(ValueError):qualify_current(bad)
        for key in GC:
            for value in [None,'foreign']:
                with self.subTest(key=key),self.assertRaises(ValueError):qualify_current(dict(GC,**{key:value}))
        for key,value in [('MainPID','430851'),('InvocationID','a14cc600a4fd4f2e9d8c4731ad9d754b'),('ExecMainCode','1'),('Result','timeout')]:
            with self.assertRaises(ValueError):qualify_current(dict(GC,**{key:value}))

    def test_actual_generated_payload_still_demands_pid1_done_and_current_twice(self):
        s=payload();ast.parse(s)
        for part in ['result=qualify(BINDING,rows,done)','currentStateClass=qualify_current(state)','if show()!=state','genuineRootDone','activeAbsent']:
            self.assertTrue(part in s,part)
        self.assertFalse('systemctl start' in s)
        self.assertFalse('pidfd_send_signal' in s)


if __name__=='__main__':unittest.main()
