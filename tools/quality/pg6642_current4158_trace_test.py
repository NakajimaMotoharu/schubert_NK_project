import unittest
import pg6642_current4158_trace as p


class CurrentOriginalTraceTest(unittest.TestCase):
    def test_actual4158_not_historical_success_addition(self):
        x=p.measurement()
        self.assertEqual(p.SOURCE,x['productionSource']);self.assertEqual('PG6634-six-v1',x['run'])
        self.assertEqual((4158,635,1667),(x['tests'],x['suites'],x['mainClasses']))
        self.assertFalse(x['nativeQualified']);self.assertFalse(x['formalAccepted'])
        self.assertEqual(0,x['acceptedLeafDelta']);self.assertIsNone(x['effortPercent'])
        self.assertEqual(dict(LINE=3478,METHOD=679,CLASS=38,BRANCH=714),x['remaining'])

    def test_historical_acceptance_and_unmeasured_native_retained(self):
        x=p.measurement()
        self.assertEqual(17,x['canonicalAcceptance']['historicalAcceptedTasks'])
        self.assertEqual([],x['runtimeVerifiedRows']);self.assertFalse(x['oldSourceNativeImported'])
        self.assertEqual(0,x['testsExecutedByTrace']);self.assertTrue(x['historicalNativeNotReauthenticated'])


if __name__=='__main__':unittest.main()
