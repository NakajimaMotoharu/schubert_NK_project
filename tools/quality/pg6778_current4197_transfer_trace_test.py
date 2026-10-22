import unittest
import pg6778_current4197_transfer_trace as p


class CurrentTransferTraceTest(unittest.TestCase):
    def test_only_genuine_current_whole_measurement(self):
        x=p.measurement()
        self.assertEqual(p.SOURCE,x['productionSource']);self.assertEqual('PG6768-six-v1',x['run'])
        self.assertEqual((4197,646,1669),(x['tests'],x['suites'],x['mainClasses']))
        self.assertFalse(x['nativeQualified']);self.assertFalse(x['formalAccepted'])
        self.assertEqual(0,x['acceptedLeafDelta']);self.assertIsNone(x['effortPercent'])

    def test_historical_acceptance_and_runtime_not_imported(self):
        x=p.measurement();self.assertEqual(17,x['canonicalAcceptance']['historicalAcceptedTasks'])
        self.assertEqual([],x['runtimeVerifiedRows']);self.assertFalse(x['oldSourceNativeImported'])
        self.assertEqual(0,x['testsExecutedByTrace']);self.assertTrue(x['historicalNativeNotReauthenticated'])

    def test_frozen_definition_has_exact_current_source_and_counts(self):
        method=p.definitions('0'*64,'0'*64)['measurement']
        self.assertEqual(p.SOURCE,method.__globals__['SOURCE'])
        self.assertIs(p.read_qualified,method.__globals__['read_qualified'])
        for value in ('PG6768-six-v1',4197,646,1669):self.assertIn(value,method.__code__.co_consts)


if __name__=='__main__':unittest.main()
