"""Pure native/A01 contract fixtures; no guest nor synthesized acceptance."""
import ast
import json
import unittest
from pathlib import Path
from unittest.mock import patch
from pg1446_current_cold_stage import W
import pg2718_operation_native_catalog as catalog
import pg2720_operation_current_a01 as a01
import pg2722_operation_native_qualification as native


class NewNativePreparation(unittest.TestCase):
    def test_actual_latest_points_require_preserved_old28_not_import(self):
        live=json.loads((W/'pg2542-strict-current-live-binding-v1/manifest.safe.json').read_bytes())
        with patch.object(catalog,'before',return_value='a'*64):raw=catalog.catalog_source("def completed(*args):raise ValueError('fixture only')",live['binding'],live['binding']['start']+1800000000)
        ast.parse(raw)
        for m in ['require(len(old)==28)','priorOldSourceTwentyEightCopiesPreserved','priorOldSourcePointsImported','pg2684-operation-current-noargs-once-v1','pg2708-native-stop-v1',native.SOURCE]:self.assertIn(m,raw)
        self.assertNotIn('require(len(old)==22)',raw)

    def test_newfull3666_all1643_no_old_resource_bridge(self):
        raw=native.server()
        for m in ['PG2722-native-v1','source-full-PG2694','runs/PG2694-six-v1','3666','len(streams)==9',native.SOURCE]:self.assertIn(m,raw)
        transport=native.source()
        for m in ['pg2718-operation-native-catalog-v1','pg2722-operation-native-qualified-v1','pg2695-expiry-fixed-full-qualified-v1']:self.assertIn(m,transport)
        self.assertNotIn('retainedQualifiedNativeReused',raw)

    def test_a01_constructs_new_actual_identity_and_unchanged_baseline_driver(self):
        original=Path.read_bytes
        fixture={'actualExit':0,'productionSource':a01.SOURCE,'rootPid':1234,'binding':{'invocation':'00000000000000000000000000000001'}}
        def read(path):
            if path==W/'pg2686-operation-current-live-binding-v1/manifest.safe.json':return json.dumps(fixture).encode()
            return original(path)
        with patch.object(Path,'read_bytes',read),patch.object(a01,'candidate_bom',return_value='a'*64):raw=a01.code()
        ast.parse(raw)
        for m in [native.SOURCE,'a'*64,'PG2654',"issued['MainPID']=='1234'",'pg2682-parent-watch-v1.private.jsonl','pg2684-operation-current-noargs-once-v1','pg2680-operation-publication-post-v1','1800000000','122dcc4c1be482ac3239325de6fb3d4bec12747d05adce3929c319ab5bdfd71d']:self.assertIn(m,raw)
        self.assertNotIn('systemctl start',raw)


if __name__=='__main__':unittest.main()
