import copy
import json
import re
import unittest
import pg3530_outbox_current_native_catalog as catalog
import pg3532_outbox_current_native_qualified as qualified
from pg1446_current_cold_stage import W


class CurrentNativeBoundaries(unittest.TestCase):
    def actual(self):
        receipt=(W/catalog.TOOLS/'pg3520_parent_receipt.py').read_text()
        binding=json.loads((W/'pg3466-outbox-current-live-binding-v1/manifest.safe.json').read_bytes())['binding']
        return receipt,binding,83898942386

    def test_current_positive_and_immutable_receipt_prefix(self):
        receipt,binding,end=self.actual();raw=catalog.catalog_source(receipt,binding,end)
        self.assertTrue(raw.startswith(receipt+'\n'))
        positive=raw[len(receipt)+1:]
        for value in ['len(old)==22','len(selected)==10', 'pg3520-native-stop-v1',
                      'pg3464-outbox-current-noargs-once-v1','82190409233','83898942386',
                      "r.get('JOB_ID')=='92576'",
                      'backup_window(backup_rows)','inspector_window(inspector_rows',
                      "set(excluded)==set(old)-{v['relative']for v in selected}"]:
            self.assertTrue(value in positive,value)
        self.assertIn('e1ee096d-370b-4ab9-915a-7c124207e854',receipt)
        for value in ['pg2246','pg2227','b2d6f605','currentBootHadNoHistoricalNative',
                      'a9cb0ac9a3a0f9bc37d0952943a98016c7a25f25']:
            self.assertNotIn(value,positive)

    def test_each_current_binding_field_and_terminal_mutation_refused(self):
        _,binding,end=self.actual()
        for key in binding:
            altered=copy.deepcopy(binding);altered[key]=None
            with self.subTest(key=key),self.assertRaises(ValueError):catalog.current(altered,end)
        for invalid in [None,True,end-1,end+1,114755353173]:
            with self.subTest(end=invalid),self.assertRaises(ValueError):catalog.current(binding,invalid)

    def test_full3712_and_saved_exec_xml_jar_scope(self):
        raw=qualified.server();source=qualified.source()
        for value in ['PG3412','PG3532','3712',"sha(B/'runs/PG3412-six-v1'/m/'jacoco.exec')",
                      "qualified['modules'][m]['coverageXmlSha256']", "qualified['jarHashes'][m]",
                      "classByteMismatch",'NativeSessions571Test', 'NativePointDominanceTest']:
            self.assertIn(value,raw)
        for value in ['PG2798','PG2908','nativeQualifiedFull','qualificationInputs']:
            self.assertNotIn(value,raw)
        for value in ['pg3530-outbox-current-native-catalog-v1','pg3414-outbox-full-qualified-v1',
                      'PG3532-native-input-v3.tar',"len(catalog['selected'])!=10"]:
            self.assertIn(value,source)

    def test_final_server_transport_tuple_and_saved_input_not_renamed(self):
        server=qualified.server();transport=qualified.source()
        pattern=r'PG3532-native-input-v[0-9]+\.tar'
        self.assertEqual({'PG3532-native-input-v3.tar'},set(re.findall(pattern,server)))
        self.assertEqual(set(re.findall(pattern,server)),set(re.findall(pattern,transport)))
        self.assertIn("original=W/'pg3532-outbox-current-native-qualified-v1'",transport)
        self.assertIn("out=W/'pg3532-outbox-current-native-qualified-v3'",transport)
        self.assertNotIn("r=subprocess.run(SSH+['sudo','-n','cat'",transport)
        for value in ['PG3532-native-input-v1.tar','PG3532-native-input-v2.tar','PG3532-native-v1','PG3532-native-v2']:
            self.assertNotIn(value,server+transport)


if __name__=='__main__':unittest.main()
