"""Actual independent header exact equality and old activation negative must survive positive bind."""
import ast
import datetime
import unittest
from pg1446_current_cold_stage import W
from pg2030_fresh_normal_warning_owned_stop_sources import TOOLS
from pg2046_receipt_preserving_current_native_catalog import catalog_source


class ReceiptPreserved(unittest.TestCase):
    def test_actual_header_unchanged_and_current_positive_old_negative_separate(self):
        receipt=(W/TOOLS/'pg2030_parent_receipt.py').read_text();raw=catalog_source(receipt)
        self.assertTrue(raw.startswith(receipt+'\n'));self.assertTrue("binding.get('activation')!='9adbf05a-61d0-408b-b51d-ab19c7e5b16a'"in raw)
        nodes=[n for n in ast.parse(receipt).body if isinstance(n,(ast.Assign,ast.FunctionDef))];ns={};exec(compile(ast.Module(body=nodes,type_ignores=[]),'<actual unchanged receipt>','exec'),ns)
        self.assertEqual('e31b627c-c0e2-4120-bd64-c0777479e800',ns['BINDING']['activation'])
        self.assertTrue('ROOT_START=106318294326'in raw and 'ROOT_END=107890801314'in raw)
        binding=ns['BINDING'];stamp=int(datetime.datetime(2026,10,13,1,25,44,tzinfo=datetime.timezone.utc).timestamp()*1000000)
        common={'_BOOT_ID':binding['boot'],'_PID':'1','_UID':'0','_COMM':'systemd','UNIT':'schubert-nk-morning-controller.service','INVOCATION_ID':binding['invocation'],'__MONOTONIC_TIMESTAMP':'106918294326','__REALTIME_TIMESTAMP':str(stamp)}
        rows=[dict(common,__CURSOR='golden-first',MESSAGE_ID='39f53479d3a045ac8e11786248231fbf',JOB_ID='187092',JOB_TYPE='start',JOB_RESULT='done'),dict(common,__CURSOR='golden-second',MESSAGE_ID='7ad2d189f7e94e70a38c781354912448')]
        done=b'NKDONE1\n4148e3e8-f107-431a-ab27-d6e6d1f1772e\n2026-10-12T18:20:32.598894Z\ne31b627c-c0e2-4120-bd64-c0777479e800\n2026-10-13T01:25:43.000000Z\n10\n'
        self.assertEqual(10,ns['completed'](rows,done)['completionCode'])
        with self.assertRaises(ValueError):ns['classify']({**binding,'activation':'9adbf05a-61d0-408b-b51d-ab19c7e5b16a'},ns['GC'],rows,done)


if __name__=='__main__':unittest.main()
