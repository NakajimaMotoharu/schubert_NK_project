import json
import unittest
from pg1446_current_cold_stage import W
from pg2021_fresh_resume_terminal_receipt_test import Receipt
import pg2188_newsource_owned_stop_sources as p


class ReceiptSource(unittest.TestCase):
    def test_actual_pure_emission_preserves_foreign_old_run_negatives(self):
        b,s,r,d=Receipt().fixture(10)
        ns={};exec(compile(p.emit_receipt({'binding':b,'rootPid':685621},s),'<actual emit independent fixture>','exec'),ns)
        self.assertEqual(ns['completed'](r,d)['completionCode'],10)
        for key,value in [('run','a31dd6da-cf4c-4d0f-ab7c-5c8bb59c0b75'),('activation','9026b2ab-bb42-49cd-a2bd-4c661049dce3')]:
            with self.assertRaises(ValueError):ns['classify'](dict(b,**{key:value}),s,r,d)
        actual=json.loads((W/'pg2180-newsource-live-binding-v1/manifest.safe.json').read_bytes())
        ns={};exec(compile(p.emit_receipt(actual,s),'<actual current emission only>','exec'),ns)
        self.assertEqual(ns['BINDING']['run'],'02bddddf-9cd3-4668-9d67-7561232fc4e4')
        # This fixture state is not an actual acceptance and no real receipt is executed.


if __name__=='__main__':unittest.main()
