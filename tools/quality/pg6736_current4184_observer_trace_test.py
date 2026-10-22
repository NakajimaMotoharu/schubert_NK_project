import unittest
import pg6736_current4184_observer_trace as p


class CurrentObserverTraceTest(unittest.TestCase):
    def test_only_genuine_current_host_measurement(self):
        x=p.measurement()
        self.assertEqual(p.SOURCE,x['productionSource'])
        self.assertEqual('PG6726-six-v1',x['run'])
        self.assertEqual((4184,643,1667),(x['tests'],x['suites'],x['mainClasses']))
        self.assertFalse(x['nativeQualified']);self.assertFalse(x['formalAccepted'])
        self.assertEqual(0,x['acceptedLeafDelta']);self.assertIsNone(x['effortPercent'])

    def test_historical_acceptance_and_runtime_not_imported(self):
        x=p.measurement()
        self.assertEqual(17,x['canonicalAcceptance']['historicalAcceptedTasks'])
        self.assertEqual([],x['runtimeVerifiedRows'])
        self.assertFalse(x['oldSourceNativeImported'])
        self.assertEqual(0,x['testsExecutedByTrace'])
        self.assertTrue(x['historicalNativeNotReauthenticated'])

    def test_explicit_frozen_definition_before_execution(self):
        d=p.definitions('0'*64,'0'*64)
        method=d['measurement']
        self.assertEqual(p.SOURCE,method.__globals__['SOURCE'])
        self.assertIs(p.read_qualified,method.__globals__['read_qualified'])
        self.assertIn('PG6726-six-v1',method.__code__.co_consts)
        self.assertIn(4184,method.__code__.co_consts)
        self.assertIn(643,method.__code__.co_consts)


if __name__=='__main__':unittest.main()
