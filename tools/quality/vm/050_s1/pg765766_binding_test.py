"""Offline inert native/post source join, no runtime/collector authority."""
import copy
import unittest
from pg764_binding_test import fixture
from pg766_native_counter import code,catalog
from pg765_terminal_final import source as post


class BindingTest(unittest.TestCase):
    def test_exact_current_host_and_genuine_native_only(self):
        proof=fixture();raw=code({},proof,{'before.private.json':'1'*64,'after.private.json':'2'*64})
        compile(raw,'<native current qualifications>', 'exec')
        for text in ('PG766-current-eight-native-v1','pg748-closing-six-host-v1',
                     'd4d3ba09651c75d15334e2775fa9a1ae8f8362e2fa92d9e8ebb57c1d8667d96e',
                     '8d4b68b4f1449932ebe506aaf08e584bbfea8dd2',"tests']==3513",'142602','137240785885','138900000000'):
            self.assertIn(text,raw)
        for old in ('pg680','pg698','pg697','pg696','pg713','pg730','1ec197','9bd505','b710c69','3489'):
            self.assertNotIn(old,raw)
        for key,value in (('actualExit',1),('actualExit',False),('actualExit',0.0),('actualExit',None),('actualExit','0'),('productionSource','9bd50536f692610036a0ed8b83e0a8b35fe2a66f'),('batchRun','8633b77f-77dc-4a78-88b4-41165f159b43')):
            bad=copy.deepcopy(proof);bad[key]=value
            with self.assertRaises(AssertionError):code({},bad,{'before.private.json':'1'*64,'after.private.json':'2'*64})
        for key in ('genuineRootDone','genuinePid1StartDone'):
            for value in (False,1,None,'true'):
                bad=copy.deepcopy(proof);bad['genuineCompletion'][key]=value
                with self.assertRaises(AssertionError):code({},bad,{'before.private.json':'1'*64,'after.private.json':'2'*64})

    def test_catalog_and_post_exact_slots(self):
        raw=catalog('1'*64);compile(raw,'<current catalog>', 'exec')
        self.assertIn('pg764-native-stop-v1',raw);self.assertNotIn('pg696',raw)
        self.assertIn('pg765-terminal-final-v1',post());self.assertIn('pg750-manifest.sig',post())


if __name__=='__main__':unittest.main()
