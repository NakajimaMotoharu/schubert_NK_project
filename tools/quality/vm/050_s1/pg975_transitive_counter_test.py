"""YKT768 indirect730->698->644->614 inherits local/whole baseline separation."""
import unittest
import pg730_native_counter as p
def proof():return {'actualExit':0,'productionSource':'1ec19782a1afe22d1de75b05f4cd12b8a8a8a172','batchRun':'55ac70e7-0180-4c32-8c91-5a379ebedf24','genuineCompletion':{'genuineRootDone':True,'genuinePid1StartDone':True,'endMonotonicUs':128549297774}}
class Test(unittest.TestCase):
    def test_transitive_generator_preserves_source_and_distinct_baselines(self):
        raw=p.code({'fixture.exec':'0'*64},proof(),{'before.private.json':'1'*64,'after.private.json':'2'*64})
        for x in ('moduleLocalCounters',"[executions[modules.index(m)]]",'executions+streams','pg713-expiry-six-host-v1','1ec19782a1afe22d1de75b05f4cd12b8a8a8a172','pg730-current-eight-native-v1'):
            self.assertIn(x,raw,'missing '+x)
    def test_indirect_profile_still_rejects_false_completion(self):
        v=proof();v['genuineCompletion']['genuineRootDone']=False
        with self.assertRaises(AssertionError):p.code({},v,{})
if __name__=='__main__':unittest.main()
