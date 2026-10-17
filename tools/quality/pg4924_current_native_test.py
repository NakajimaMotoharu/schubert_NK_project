import copy
import inspect
import json
import unittest
from unittest.mock import patch
from pyflakes.api import check,checkPath
import pg4924_current_native_catalog as catalog
import pg4926_current_native_qualified as native


class Native(unittest.TestCase):
    def test_strict_actual_current_whole_class_delta_no_old_source_native(self):
        value=json.loads((native.W/native.FULL/'manifest.safe.json').read_bytes());q=native.qualify(value)
        self.assertEqual(1647,len(q['allPhysicalMainSha256']))
        for key,badvalue in [('tests',3739),('suites',549),('mainClasses',1646),('actualExit',True),('oldNativeImported',True),('productionSource',catalog.previous.role.SOURCE),('changedClasses',[]),('allSixFormatBeforeAnyPt',False)]:
            bad=copy.deepcopy(value);bad['result'][key]=badvalue
            with self.subTest(key=key),self.assertRaises(ValueError):native.qualify(bad)

    def test_actual_full11_catalog_archive72_and_exact_server_new3761(self):
        # Source-only catalog assembly, no actual stop/stream qualification claim.
        with patch.object(catalog.role.admission,'before',return_value='a'*64):raw=catalog.catalog_source('def completed(*args):raise ValueError("not executed")',catalog.role.admission.live(),198238760299)
        self.assertEqual(0,check('SEALS={}\n'+raw,'<complete current full11 catalog>'))
        for text in ("len(frozen['rows'])==24",'==72','all72BeforeCopiesPreserved',catalog.role.SOURCE,catalog.role.BOM):self.assertIn(text,raw)
        self.assertNotIn("frozen['database']",raw)
        server=native.server();self.assertIn('PG4844-six-v1',server);self.assertNotIn('PG4694',server);self.assertIn('PG4926-native-v1',server);self.assertIn('3761',server)
        self.assertIn('test ! -e /home/mini/schubert-nk-pgpt/transfer/PG4926-native-input-v1.tar',native.source())
        coordinates=native.previous.transport.prior.previous.entry().__globals__['coordinates']
        complete='import xml.etree.ElementTree as ET\nCOUNTERS=("LINE","METHOD","CLASS","BRANCH")\nARCHIVE_SHA="'+('a'*64)+'"\n'+inspect.getsource(coordinates)+'\n'+server
        self.assertEqual(0,check(complete,'<all1647 full native server namespace>'))
        for path in (catalog.__file__,native.__file__,__file__):self.assertEqual(0,checkPath(path))


if __name__=='__main__':unittest.main()
