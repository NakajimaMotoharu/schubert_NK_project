import unittest
import pg6872_current4209_trace as p


class Current4209TraceTest(unittest.TestCase):
    def test_genuine_current_original_only(self):
        x=p.measurement()
        self.assertEqual((p.SOURCE,'PG6862-six-v1',4209,653,1669),(x['productionSource'],x['run'],x['tests'],x['suites'],x['mainClasses']))
        self.assertFalse(x['nativeQualified']);self.assertFalse(x['formalAccepted'])
        self.assertEqual(0,x['acceptedLeafDelta']);self.assertIsNone(x['effortPercent'])

    def test_historical17_and_no_runtime_or_old_native_import(self):
        x=p.measurement()
        self.assertEqual(17,x['canonicalAcceptance']['historicalAcceptedTasks'])
        self.assertEqual([],x['runtimeVerifiedRows']);self.assertFalse(x['oldSourceNativeImported'])
        self.assertEqual(0,x['testsExecutedByTrace']);self.assertTrue(x['historicalNativeNotReauthenticated'])


if __name__=='__main__':unittest.main()
