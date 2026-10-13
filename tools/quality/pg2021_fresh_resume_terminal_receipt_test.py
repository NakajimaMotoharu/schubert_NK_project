"""Independent SUCCESS/WARNING normal Unit and foreign/null/old/timing error vectors."""
import copy
import datetime
import unittest
from pg2021_fresh_resume_terminal_receipt import classify,payload


class Receipt(unittest.TestCase):
    def fixture(self,code):
        binding={'boot':'fixedboot','invocation':'fixedinvocation','job':'17','start':100000000,'run':'fixedrun','cutoff':'2026-10-12T18:20:32.598894Z','activation':'newactivation'}
        state={'ActiveState':'inactive','SubState':'dead','MainPID':'0','ControlPID':'0','Job':'','Result':'success','ExecMainCode':'1','ExecMainStatus':str(code),'InvocationID':'fixedinvocation','SuccessExitStatus':'10','ExecMainStartTimestampMonotonic':'100000000','ExecMainExitTimestampMonotonic':'700000000'}
        stamp=int(datetime.datetime(2026,10,13,1,30,1,tzinfo=datetime.timezone.utc).timestamp()*1000000)
        common={'_BOOT_ID':'fixedboot','_PID':'1','_UID':'0','_COMM':'systemd','UNIT':'schubert-nk-morning-controller.service','INVOCATION_ID':'fixedinvocation','__MONOTONIC_TIMESTAMP':'700001000','__REALTIME_TIMESTAMP':str(stamp)}
        rows=[dict(common,__CURSOR='first',MESSAGE_ID='39f53479d3a045ac8e11786248231fbf',JOB_ID='17',JOB_TYPE='start',JOB_RESULT='done'),dict(common,__CURSOR='second',MESSAGE_ID='7ad2d189f7e94e70a38c781354912448')]
        done=('NKDONE1\nfixedrun\n2026-10-12T18:20:32.598894Z\nnewactivation\n2026-10-13T01:30:00.000000Z\n'+str(code)+'\n').encode()
        return binding,state,rows,done

    def test_both_normal_codes_and_resumed_original_cutoff(self):
        for code,outcome in [(0,'SUCCESS'),(10,'WARNING')]:
            result=classify(*self.fixture(code));self.assertEqual(outcome,result['completionOutcome']);self.assertEqual(600,result['elapsedSeconds'])
        payload(self.fixture(10)[0])

    def test_state_and_journal_foreign_fields_and_missing(self):
        binding,state,rows,done=self.fixture(10)
        for key in state:
            for value in [None,'foreign']:
                with self.assertRaises(ValueError):classify(binding,dict(state,**{key:value}),rows,done)
        for key in rows[0]:
            bad=copy.deepcopy(rows);bad[0][key]='second'if key=='__CURSOR'else'foreign'
            with self.assertRaises(ValueError):classify(binding,state,bad,done)
        for bad in [None,[],rows+[rows[0]],[dict(r,__MONOTONIC_TIMESTAMP='1900000001')for r in rows]]:
            with self.assertRaises(ValueError):classify(binding,state,bad,done)

    def test_done_old_activation_code_and_parent_timeout_rejected(self):
        binding,state,rows,done=self.fixture(10)
        for bad in [None,b'',done[:-1],done.replace(b'newactivation',b'oldactivation'),done.replace(b'\n10\n',b'\n143\n'),done.replace(b'01:30:00',b'01:32:00')]:
            with self.assertRaises(ValueError):classify(binding,state,rows,bad)
        with self.assertRaises(ValueError):classify(dict(binding,activation='9adbf05a-61d0-408b-b51d-ab19c7e5b16a'),state,rows,done)
        with self.assertRaises(ValueError):classify(binding,dict(state,ExecMainExitTimestampMonotonic='1900000001'),rows,done)


if __name__=='__main__':unittest.main()
