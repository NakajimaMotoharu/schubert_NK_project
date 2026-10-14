"""Exact actual host full input/newpoint graph, oldsource and oldcounts forbidden."""
import inspect
import io
import unittest
from pyflakes.api import check
from pyflakes.reporter import Reporter
import pg2908_network_current_native_qualification as p


class CurrentQualification(unittest.TestCase):
    def test_server_host3680_and_transport_currentpoints(self):
        a=p.server();b=p.source()
        extractor=p.prior.previous.entry().__globals__['coordinates']
        complete='import xml.etree.ElementTree as ET\nCOUNTERS=("LINE","METHOD","CLASS","BRANCH")\nARCHIVE_SHA="a"\n'+inspect.getsource(extractor)+'\n'+a
        self.assertEqual(0,check(complete,'<whole current actual CRC server>'))
        self.assertNotIn('import xml.etree.ElementTree as ET',a)
        for v in ['PG2798','full[\'tests\']==3680','qualificationInputs','jarHashes','NativeSessions571Test','NativePointDominanceTest']:
            self.assertTrue(v in a,v)
        for v in ['PG2694','3666','PG2722']:self.assertFalse(v in a,v)
        self.assertIn('PG2908-native-v2',a)
        for v in ['pg2906-network-current-native-catalog-v1','pg2908-network-current-native-qualified-v2','pg2800-jdbc-null-fixed-full-qualified-v1','PG2908-native-input-v2.tar']:
            self.assertTrue(v in b,v)
        self.assertFalse('pg2718-operation-native-catalog-v1'in b)
        self.assertTrue("'tests':3680,'suites':542,'mainClasses':1643"in inspect.getsource(p.qualify_snapshot))

    def test_actual_caller_header_missing_and_duplicate_are_rejected(self):
        extractor=p.prior.previous.entry().__globals__['coordinates']
        body='ARCHIVE_SHA="a"\n'+inspect.getsource(extractor)+'\n'+p.server()
        header='import xml.etree.ElementTree as ET\nCOUNTERS=("LINE","METHOD","CLASS","BRANCH")\n'
        report=Reporter(io.StringIO(),io.StringIO())
        self.assertEqual(0,check(header+body,'<actual caller>',report))
        self.assertGreater(check(body,'<missing caller imports>',report),0)
        self.assertGreater(check(header+'import xml.etree.ElementTree as ET\n'+body,'<original duplicate import>',report),0)
        self.assertTrue("source='import xml.etree.ElementTree as ET\\nCOUNTERS="in p.source())


if __name__=='__main__':unittest.main()
