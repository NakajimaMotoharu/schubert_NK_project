import unittest
import pg6678_current4170_trace as p


class CurrentOriginalTraceTest(unittest.TestCase):
    def test_only_genuine_current_host_measurement_not_historical_native(self):
        x=p.measurement()
        self.assertEqual(p.SOURCE,x['productionSource']);self.assertEqual('PG6668-six-v1',x['run'])
        self.assertEqual((4170,638,1667),(x['tests'],x['suites'],x['mainClasses']))
        self.assertFalse(x['nativeQualified']);self.assertFalse(x['formalAccepted'])
        self.assertEqual(0,x['acceptedLeafDelta']);self.assertIsNone(x['effortPercent'])

    def test_acceptance_and_unmeasured_runtime_remain_separate(self):
        x=p.measurement()
        self.assertEqual(17,x['canonicalAcceptance']['historicalAcceptedTasks'])
        self.assertEqual([],x['runtimeVerifiedRows']);self.assertFalse(x['oldSourceNativeImported'])
        self.assertEqual(0,x['testsExecutedByTrace']);self.assertTrue(x['historicalNativeNotReauthenticated'])


if __name__=='__main__':unittest.main()
