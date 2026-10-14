"""Actual whole catalog: separate receipt negatives, ten current points and retained copies."""
import json
import unittest
from pg1446_current_cold_stage import W
import pg3022_current_resume_native_catalog as catalog


class CurrentNative(unittest.TestCase):
    def test_actual_current_window_and_all_retained_copy_checks(self):
        receipt = (W / 'pg3006-current-resume-owned-stop-tools-v1/pg3006_parent_receipt.py').read_text()
        live = json.loads((W / 'pg2990-current-resume-live-binding-v1/manifest.safe.json').read_bytes())
        term = json.loads((W / 'pg2992-current-resume-terminal-v1/manifest.safe.json').read_bytes())
        raw = catalog.catalog_source(receipt, live['binding'], term['endMonotonicUs'])
        self.assertTrue(raw.startswith(receipt + '\n'))
        for s in ['len(selected)==10', 'len(old)==10', '18100986959', '19749542200', '79a3260ae16d42bf942ab914ed144c28', 'pg2984-current-fresh-resume-once-v1', 'pg3006-native-stop-v1', 'c1170b22495c28a114640f2f1153c92c9fa673431b0fc35e4e0039d0ca9cb510', "issued['manifestSha256']==CURRENT_BOM", 'backup_window(backup_rows)', 'inspector_window(inspector_rows']:
            self.assertTrue(s in raw, s)
        self.assertFalse('b2d6f605' in raw)
        self.assertFalse('pg2356-current-runtime-verification-post-v1' in raw)
        self.assertTrue('91f5484b-9702-4c7c-97f3-dd5110a853f9' in receipt)
        self.assertTrue('oldNativeImported' in raw)


if __name__ == '__main__':
    unittest.main()
