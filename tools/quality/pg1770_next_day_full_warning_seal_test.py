"""No failed PID1 Job converted into done/success; strict same-generation budget."""
import unittest
from pg1770_next_day_full_warning_seal import warning_completion,payload


class Seal(unittest.TestCase):
    def test_failure_warning_is_separate_from_success(self):
        common={'_BOOT_ID':'3d69f5af6bac46b1a5407591c4a79a0d','_PID':'1','_UID':'0','_COMM':'systemd','UNIT':'schubert-nk-morning-controller.service','INVOCATION_ID':'b5a12ee25dc44ec49b08f5d084b4052f','__MONOTONIC_TIMESTAMP':'83018954600'}
        rows=[{**common,'MESSAGE_ID':'be02cf6855d2428ba40df7e9d022f03d','JOB_ID':'127250','JOB_TYPE':'start','JOB_RESULT':'failed','__REALTIME_TIMESTAMP':'1791830846800000'},{**common,'MESSAGE_ID':'98e322203f7a4ed290d09fe03c09fe15','EXIT_CODE':'exited','EXIT_STATUS':'10'}]
        done=b'NKDONE1\n4148e3e8-f107-431a-ab27-d6e6d1f1772e\n2026-10-12T18:20:32.598894Z\n9adbf05a-61d0-408b-b51d-ab19c7e5b16a\n2026-10-12T18:47:26.7Z\n10\n'
        result=warning_completion(rows,done)
        self.assertTrue(result['genuinePid1Failure']);self.assertFalse(result['genuinePid1StartDone']);self.assertFalse(result['wholeAccepted'])
        for key,value in [('JOB_RESULT','done'),('JOB_ID','old'),('_PID','2'),('INVOCATION_ID','old'),('__MONOTONIC_TIMESTAMP','83204764714')]:
            bad=[{**rows[0],key:value},rows[1]]
            with self.assertRaises(ValueError):warning_completion(bad,done)
        with self.assertRaises(ValueError):warning_completion(rows+rows[:1],done)
        with self.assertRaises(ValueError):warning_completion(rows,done[:-3]+b'0\n')

    def test_actual_payload_independent_sources_and_no_operation(self):
        raw=payload();self.assertIn('pg1768-next-day-inbox-oracle-v1/oracle.private.json',raw)
        self.assertNotIn('pg1699-new-current-ordinary-once-v1/before.private.json',raw)
        self.assertNotIn('pidfd_send_signal',raw)


if __name__=='__main__':unittest.main()
