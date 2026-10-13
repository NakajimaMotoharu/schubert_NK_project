import copy
import unittest
from pyflakes.api import check
from pg2208_current_newboot_cold_sources import BOOT
import pg2254_newboot_native_catalog as p


class NativeCurrentWindows(unittest.TestCase):
    def test_dynamic_same_generation_and_independent_normal_order(self):
        common={'_BOOT_ID':BOOT.replace('-',''),'_PID':'1','_UID':'0','_COMM':'systemd','UNIT':'schubert-nk-inbox-inspector.service','INVOCATION_ID':'1'*32}
        rows=[dict(common,__CURSOR=str(i),__MONOTONIC_TIMESTAMP=str(100+i),MESSAGE_ID=m,**x)for i,(m,x)in enumerate([
          ('7d4958e842da4a758f6c1cdc7b36dcc5',{'JOB_ID':'7','JOB_TYPE':'start'}),('39f53479d3a045ac8e11786248231fbf',{'JOB_ID':'7','JOB_TYPE':'start','JOB_RESULT':'done'}),('7ad2d189f7e94e70a38c781354912448',{}),('9d1aaa27d60140bd96365438aad20286',{'JOB_ID':'8','JOB_TYPE':'stop','JOB_RESULT':'done'})])]
        self.assertEqual((100,102,'1'*32),p.inspector_window(rows,BOOT.replace('-',''),90,110))
        for field,value in [('_BOOT_ID','old'),('INVOCATION_ID','2'*32),('JOB_ID','8'),('__MONOTONIC_TIMESTAMP','89'),('__CURSOR','1'),('JOB_RESULT','failed')]:
            bad=copy.deepcopy(rows);bad[0][field]=value
            with self.assertRaises(ValueError):p.inspector_window(bad,BOOT.replace('-',''),90,110)
        for bad in [None,[],rows[:-1],rows+[rows[0]]]:
            with self.assertRaises(ValueError):p.inspector_window(bad,BOOT.replace('-',''),90,110)
        for boot,start,end in [(None,90,110),(BOOT,90,110),(BOOT.replace('-',''),True,110),(BOOT.replace('-',''),90,89),(BOOT.replace('-',''),90,1800000091)]:
            with self.assertRaises(ValueError):p.inspector_window(rows,boot,start,end)
        binding={'activation':'22222222-2222-4222-8222-222222222222','start':1000000,'job':'17'}
        raw=p.catalog_source('def completed(*args):return {}\n',binding,1000001)
        self.assertEqual(0,check('SEALS={}\n'+raw,'<actual whole currentboot native>'))
        self.assertIn('oldNativeImported',raw);self.assertIn('currentBootHadNoHistoricalNative',raw)
        self.assertNotIn('3d69f5af',raw);self.assertNotIn('len(old)==32',raw)
        self.assertIn('len(selected)==10',raw)


if __name__=='__main__':unittest.main()
