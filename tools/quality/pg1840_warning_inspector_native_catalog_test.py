"""Independent literal Inspector PID1 vector and emitted current-only classification."""
import copy
import unittest
from pg1840_warning_inspector_native_catalog import inspector_window,catalog_source


class Inspector(unittest.TestCase):
    def test_fixed_actual_generation_and_rejected_foreign_failed_missing(self):
        base={'_BOOT_ID':'3d69f5af6bac46b1a5407591c4a79a0d','_PID':'1','_UID':'0','_COMM':'systemd','UNIT':'schubert-nk-inbox-inspector.service','INVOCATION_ID':'6c5bf1041fdf45d992dd2b58afd7df09'}
        rows=[dict(base,__CURSOR='a',__MONOTONIC_TIMESTAMP='81623098577',MESSAGE_ID='7d4958e842da4a758f6c1cdc7b36dcc5',JOB_ID='127856',JOB_TYPE='start'),dict(base,__CURSOR='b',__MONOTONIC_TIMESTAMP='81634285835',MESSAGE_ID='39f53479d3a045ac8e11786248231fbf',JOB_ID='127856',JOB_TYPE='start',JOB_RESULT='done'),dict(base,__CURSOR='c',__MONOTONIC_TIMESTAMP='81635354035',MESSAGE_ID='7ad2d189f7e94e70a38c781354912448'),dict(base,__CURSOR='d',__MONOTONIC_TIMESTAMP='81635354860',MESSAGE_ID='9d1aaa27d60140bd96365438aad20286',JOB_ID='128003',JOB_TYPE='stop',JOB_RESULT='done')]
        self.assertEqual((81623098577,81635354035),inspector_window(rows))
        for key,bad in [('_PID','2'),('UNIT','foreign'),('INVOCATION_ID','a'*32),('__CURSOR','b'),('__MONOTONIC_TIMESTAMP','81404764712'),('JOB_RESULT','failed'),('JOB_ID','128003')]:
            changed=copy.deepcopy(rows);changed[0][key]=bad
            with self.subTest(key=key),self.assertRaises(ValueError):inspector_window(changed)
        for bad in [None,[],rows[:-1],rows+rows[:1]]:
            with self.assertRaises(ValueError):inspector_window(bad)

    def test_emitted_nine_and_explicit_nonimported_point(self):
        raw=catalog_source('def completed(rows,original): return {}\n')
        self.assertIn('len(selected)==9',raw);self.assertIn('len(old)==20',raw)
        self.assertIn("hashlib.sha256(early_bytes).hexdigest()==closing_item['sha256']",raw)
        self.assertIn("or relative==earlier:continue",raw)
        self.assertIn('sameSessionEarlierPointNotImported',raw)
        self.assertFalse('len(selected)==8'in raw)


if __name__=='__main__':unittest.main()
