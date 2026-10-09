"""Offline inert native/post source join, no runtime/collector authority."""
import copy
import unittest
from pg728_binding_test import fixture
from pg730_native_counter import code,catalog
from pg729_terminal_final import source as post


class BindingTest(unittest.TestCase):
    def test_exact_current_host_and_genuine_native_only(self):
        proof=fixture();raw=code({},proof,{'before.private.json':'1'*64,'after.private.json':'2'*64})
        compile(raw,'<native current qualifications>', 'exec')
        for text in ('PG730-current-eight-native-v1','pg713-expiry-six-host-v1',
                     '5f6a57015fb30d8f2097e594370d558ac6202a9d5d2ed98ce0108494cc7f524a',
                     '1ec19782a1afe22d1de75b05f4cd12b8a8a8a172',"tests']==3502",'132812','127549297774','129000000000'):
            self.assertIn(text,raw)
        for old in ('pg680','pg698','pg697','pg696','9bd505','b710c69','3489'):
            self.assertNotIn(old,raw)
        for key,value in (('actualExit',1),('productionSource','9bd50536f692610036a0ed8b83e0a8b35fe2a66f'),('batchRun','8633b77f-77dc-4a78-88b4-41165f159b43')):
            bad=copy.deepcopy(proof);bad[key]=value
            with self.assertRaises(AssertionError):code({},bad,{'before.private.json':'1'*64,'after.private.json':'2'*64})

    def test_catalog_and_post_exact_slots(self):
        raw=catalog('1'*64);compile(raw,'<current catalog>', 'exec')
        self.assertIn('pg728-native-stop-v1',raw);self.assertNotIn('pg696',raw)
        self.assertIn('pg729-terminal-final-v1',post());self.assertIn('pg715-manifest.sig',post())


if __name__=='__main__':unittest.main()
