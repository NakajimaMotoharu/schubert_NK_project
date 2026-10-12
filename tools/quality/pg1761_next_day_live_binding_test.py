"""Independent typed/current day/owner observations; no observed identities hardcoded."""
import copy
import unittest
from pg1761_next_day_live_binding import captured_parent,body,SOURCE

class Binding(unittest.TestCase):
    def test_independent_complete_and_wrong_type_owner_source_fields(self):
        expected={'MainPID':'314159','InvocationID':'1'*32,'Job':'41','ExecMainStartTimestampMonotonic':'3141590000'}
        start={'actualExit':0,'payloadSha256':'a'*64,'guest':{**expected,'clientExit':0,'ordinaryNoargs':True,'oldCompletedRunNotResumed':True,'originalBudgetSeconds':1800}}
        before={'actualExit':0,'guest':{'actualExit':0,'productionSource':SOURCE,'whole24Full32Signed187AndResourcesUnchanged':True,'todayBatchRows':0,'investigationBusinessDay':'2026-10-13','startAuthority':False}}
        self.assertEqual(expected,captured_parent(start,before,'a'*64))
        for k in expected:
            for bad in (None,False,'0','unknown'):
                d=copy.deepcopy(start);d['guest'][k]=bad
                with self.assertRaises(ValueError):captured_parent(d,before,'a'*64)
        for k,bad in [('actualExit',False),('productionSource','b'*40),('whole24Full32Signed187AndResourcesUnchanged',False),('todayBatchRows',1),('todayBatchRows',False),('investigationBusinessDay','2026-10-12'),('startAuthority',True)]:
            d=copy.deepcopy(before);d['guest'][k]=bad
            with self.assertRaises(ValueError):captured_parent(start,d,'a'*64)
        for bad in (None,'b'*64,'A'*64,''):
            with self.assertRaises(ValueError):captured_parent(start,before,bad)
        self.assertIn("date().isoformat()=='2026-10-13'",body())
        self.assertNotIn('pidfd_send_signal',body())

if __name__=='__main__':unittest.main()
