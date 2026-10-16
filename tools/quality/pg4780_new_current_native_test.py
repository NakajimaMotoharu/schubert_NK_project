"""Strict genuine same-source whole, normal full11/64 admission and exact server paths."""
import copy
import json
import unittest
from pyflakes.api import check,checkPath
from pg4752_new_current_admission_test import NewAdmission
import pg4780_new_current_native_catalog as catalog
import pg4782_new_current_native_qualified as native


class Native(unittest.TestCase):
    def test_strict_actual_whole_and_old_source_or_incomplete_delta_refused(self):
        value=json.loads((native.W/native.FULL/'manifest.safe.json').read_bytes())
        qualified=native.qualify(value);self.assertEqual(1646,len(qualified['allPhysicalMainSha256']))
        for key,badvalue in [('tests',3721),('suites',545),('mainClasses',1644),('actualExit',True),('oldNativeImported',True),('productionSource',catalog.previous.role.SOURCE),('changedClasses',[])]:
            bad=copy.deepcopy(value);bad['result'][key]=badvalue
            with self.subTest(key=key),self.assertRaises(ValueError):native.qualify(bad)
        bad=copy.deepcopy(value);bad['result']['changedClasses'][0]['action']='ADDED_INTERNAL_INTERFACE'
        with self.assertRaises(ValueError):native.qualify(bad)

    def test_catalog_full11_and_exact_new_server_source(self):
        raw=catalog.catalog_source('def completed(*args):raise ValueError("not executed")',NewAdmission().binding(),188007981413)
        self.assertEqual(0,check('SEALS={}\n'+raw,'<all current catalog>'))
        self.assertIn("len(frozen['rows'])==24",raw);self.assertNotIn("frozen['database']",raw)
        self.assertIn('==64',raw);self.assertIn('all64BeforeCopiesPreserved',raw)
        self.assertIn(catalog.role.SOURCE,raw);self.assertIn(catalog.role.BOM,raw)
        server=native.server();self.assertIn('PG4694-six-v1',server);self.assertNotIn('PG3412',server)
        self.assertIn('PG4782-native-v1',server);self.assertIn('3739',server)
        self.assertIn('test ! -e /home/mini/schubert-nk-pgpt/transfer/PG4782-native-input-v1.tar',native.source())
        self.assertEqual(0,checkPath(catalog.__file__));self.assertEqual(0,checkPath(native.__file__))


if __name__=='__main__':unittest.main()
