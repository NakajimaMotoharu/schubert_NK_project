"""Independent literal WARNING and negative generation/budget contract."""
import unittest
from pg1764_warning_terminal_capture import classify,payload


class Warning(unittest.TestCase):
    def test_actual_literal_and_each_inconsistent_field(self):
        state={'ActiveState':'failed','SubState':'failed','MainPID':'0','Result':'exit-code','ExecMainCode':'1','ExecMainStatus':'10','InvocationID':'b5a12ee25dc44ec49b08f5d084b4052f','SuccessExitStatus':'','ExecMainStartTimestampMonotonic':'81404764713','ExecMainExitTimestampMonotonic':'83018952135'}
        fields=['NKDONE1','4148e3e8-f107-431a-ab27-d6e6d1f1772e','2026-10-12T18:20:32.598894Z','9adbf05a-61d0-408b-b51d-ab19c7e5b16a','2026-10-12T18:47:26.7Z','10']
        self.assertEqual(1614.187422,classify(state,fields)['elapsedSeconds'])
        self.assertFalse(classify(state,fields)['wholeAccepted'])
        for key in state:
            with self.subTest(key=key),self.assertRaises(ValueError):classify({**state,key:'UNKNOWN'},fields)
        for i in range(6):
            wrong=list(fields);wrong[i]='INVALID'
            with self.subTest(i=i),self.assertRaises(ValueError):classify(state,wrong)
        for end in ['81404764712','83204764714',None,True]:
            with self.assertRaises(ValueError):classify({**state,'ExecMainExitTimestampMonotonic':end},fields)

    def test_generated_readonly_payload(self):
        raw=payload()
        self.assertNotIn('pidfd_send_signal',raw)
        self.assertNotIn("['systemctl','start'",raw)
        self.assertNotIn("['systemctl','stop'",raw)
        self.assertIn('wholeAccepted',raw)


if __name__=='__main__':unittest.main()
