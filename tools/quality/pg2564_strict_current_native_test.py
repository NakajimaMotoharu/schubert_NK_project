import ast
import json
import unittest
from pathlib import Path
from pg1446_current_cold_stage import W
from pg2562_strict_current_native_catalog import catalog_source
from pg2564_strict_current_native_qualification import SOURCE, ARTIFACT, result_changes, server, source
import pg2474_question_native_qualified_results as historical


class FreshNative(unittest.TestCase):
    def test_all_points_actual_binding_old_twenty_two_excluded(self):
        live = json.loads((W / 'pg2542-strict-current-live-binding-v1/manifest.safe.json').read_bytes())
        raw = catalog_source("def completed(*args):raise ValueError('fixture only')", live['binding'], live['binding']['start'] + 1800000000)
        ast.parse(raw)
        for marker in ['len(old)==22', 'priorOldSourceTwentyTwoCopiesPreserved',
                       'priorOldSourcePointsImported', 'pg2540-strict-current-noargs-once-v1',
                       'pg2554-native-stop-v1', SOURCE, 'ROOT_START=' + str(live['binding']['start'])]:
            self.assertIn(marker, raw)
        self.assertNotIn('len(old)==16', raw)

    def test_latest_nine_all1643_fresh_source_and_full3650_not_old_native(self):
        raw = server()
        for marker in ['PG2564-native-v1', 'source-full-PG2510', 'runs/PG2510-six-v1',
                       SOURCE, '3650', 'len(streams)==9', 'NativePointDominance', 'inspectorLatestClosingOnly']:
            self.assertIn(marker, raw)
        for marker in ['pg2562-strict-current-native-catalog-v1', 'pg2564-strict-current-native-qualified-v1',
                       'pg2511-strict-reference-full-qualified-v1']:
            self.assertIn(marker, source())

    def test_only_fixed_dif_a01_output_allowed_and_credential_or_input_refused(self):
        artifact = Path(historical.ARTIFACT).read_bytes(); baseline = Path(historical.BASELINE).read_bytes()
        # Historical data supplies the independently literal A01 vector/schema,
        # not actual new receipt. The actual gate reads the new actual receipt.
        receipt = json.loads((W / 'pg2470-chr-a01-native-v1.safe.json').read_bytes())
        receipt['productionSource'] = SOURCE
        result_changes([ARTIFACT], artifact, baseline, receipt)
        for paths in [[historical.ARTIFACT], [ARTIFACT, ARTIFACT], [historical.BASELINE], ['src/foreign.java'], None]:
            with self.assertRaises(ValueError):
                result_changes(paths, artifact, baseline, receipt)
        for key, value in [('actualExit',False), ('rawCookieTokenExported',True), ('productionSource','old'), ('baselineSha256','0'*64)]:
            with self.assertRaises(ValueError):
                result_changes([ARTIFACT], artifact, baseline, {**receipt,key:value})


if __name__ == '__main__':
    unittest.main()
