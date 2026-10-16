"""Independent same-source host authority and emitted complete native scope."""
import copy
import json
import unittest
from pyflakes.api import checkPath
import pg4662_current_native_qualified as native
from pg1446_current_cold_stage import W


class NativeQualification(unittest.TestCase):
    def test_actual_full_strict_authority_and_rejections(self):
        value=json.loads((W/native.FULL/'manifest.safe.json').read_bytes())
        self.assertEqual(1644,native.qualify(value)['mainClasses'])
        for key in ['productionSource','tests','suites','mainClasses','FESFlakyNotRun','staticSixModules','allOriginalCaseIdentitiesRetained','allPhysicalMainSha256','changedClasses','oldNativeImported']:
            bad=copy.deepcopy(value);bad['result'].pop(key)
            with self.subTest(key=key),self.assertRaises(ValueError):native.qualify(bad)
        bad=copy.deepcopy(value);bad['result']['mainClasses']=True
        with self.assertRaises(ValueError):native.qualify(bad)

    def test_current_server_and_transport_no_old_cache(self):
        server=native.server();source=native.source()
        self.assertIn(native.SOURCE,server);self.assertNotIn(native.template.SOURCE,server)
        self.assertIn('full[\'tests\']==3721',server);self.assertIn('source-full-PG4420',server)
        self.assertIn('classByteMismatch',server);self.assertIn('NativeSessions571',server);self.assertIn('NativePointDominance',server)
        self.assertIn('len(streams)==9',server);self.assertIn('len(v[\'selected\'])==10',server)
        self.assertIn(native.catalog.SLOT,source);self.assertIn(native.FULL,source);self.assertIn(native.SLOT,source)
        self.assertIn('test ! -e /home/mini/schubert-nk-pgpt/runs/PG4662-native-v1',source)
        self.assertNotIn("original=W/",source);self.assertIn('for i,v in enumerate(catalog[\'selected\']):',source)
        self.assertEqual(0,checkPath(native.__file__));self.assertEqual(0,checkPath(__file__))


if __name__=='__main__':unittest.main()
