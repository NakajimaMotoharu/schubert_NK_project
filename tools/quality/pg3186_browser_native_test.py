"""Independent current generation/retained-copy/whole source transport checks."""
import copy
import json
import unittest
from pg1446_current_cold_stage import W
import pg3186_browser_native_catalog as catalog
import pg3188_browser_native_qualified as qualified


class BrowserNative(unittest.TestCase):
    def test_complete_positive_body_and_immutable_receipt(self):
        receipt = (W / 'pg3150-browser-business-owned-stop-tools-v1/pg3150_parent_receipt.py').read_text()
        binding = json.loads((W / 'pg3124-browser-resume-live-binding-v1/manifest.safe.json').read_bytes())['binding']
        end = 29802580271
        raw = catalog.catalog_source(receipt, binding, end)
        self.assertTrue(raw.startswith(receipt + '\n'))
        body = raw[len(receipt)+1:]
        for literal in ['len(old)==16', 'len(selected)==10', 'pg3150-native-stop-v1',
                        'pg3144-current-parent-receipt-resume-once-v1', catalog.BEFORE,
                        catalog.NATIVE, 'snapshot=frozen', '28121423183', str(end),
                        '323bc9ad-1528-449a-8067-19228ee1e046', "r.get('JOB_ID')=='60559'",
                        'backup_window(backup_rows)', 'inspector_window(inspector_rows',
                        "set(excluded)==set(old)-{v['relative']for v in selected}"]:
            self.assertTrue(literal in body, literal)
        for old in ['pg3006', 'pg2984', 'pg2964', '0ac69fb7-3cb7-4d33-b2d9-4733fba5a4cf']:
            self.assertFalse(old in body, old)
        for name in binding:
            altered = copy.deepcopy(binding); altered[name] = None
            with self.assertRaises(ValueError):
                catalog.current(altered, end)
        for invalid in [None, True, end-1, end+1, 19749542200]:
            with self.assertRaises(ValueError):
                catalog.current(binding, invalid)

    def test_whole3691_server_and_closed_namespace(self):
        from pyflakes.api import check
        import inspect
        ns = qualified.entry().__globals__
        source = 'import xml.etree.ElementTree as ET\nCOUNTERS=("LINE","METHOD","CLASS","BRANCH")\nARCHIVE_SHA="' + 'a'*64 + '"\n' + inspect.getsource(ns['coordinates']) + '\n' + qualified.server()
        self.assertEqual(0, check(source, '<complete current Browser native server>'))
        compile(source, '<complete native server>', 'exec')
        for literal in ['PG3188', 'PG3054', '3691']:
            self.assertTrue(literal in source, literal)
        for literal in ['pg3186-browser-native-catalog-v1', 'pg3056-boundary-group-full-qualified-v1', 'PG3188-native-input-v1.tar']:
            self.assertTrue(literal in qualified.source(), literal)


if __name__ == '__main__':
    unittest.main()
