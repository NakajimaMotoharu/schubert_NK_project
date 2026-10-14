"""Exact actual host full input/newpoint graph, oldsource and oldcounts forbidden."""
import inspect
import unittest
from pyflakes.api import check
import pg2908_network_current_native_qualification as p


class CurrentQualification(unittest.TestCase):
    def test_server_host3680_and_transport_currentpoints(self):
        a=p.server();b=p.source()
        extractor=p.prior.previous.entry().__globals__['coordinates']
        self.assertEqual(0,check('ARCHIVE_SHA="a"\n'+inspect.getsource(extractor)+'\n'+a,'<whole current actual CRC server>'))
        for v in ['PG2798','full[\'tests\']==3680','qualificationInputs','jarHashes','NativeSessions571Test','NativePointDominanceTest']:
            self.assertTrue(v in a,v)
        for v in ['PG2694','3666','PG2722']:self.assertFalse(v in a,v)
        for v in ['pg2906-network-current-native-catalog-v1','pg2908-network-current-native-qualified-v1','pg2800-jdbc-null-fixed-full-qualified-v1']:
            self.assertTrue(v in b,v)
        self.assertFalse('pg2718-operation-native-catalog-v1'in b)
        self.assertTrue("'tests':3680,'suites':542,'mainClasses':1643"in inspect.getsource(p.qualify_snapshot))


if __name__=='__main__':unittest.main()
