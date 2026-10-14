import hashlib
import json
import unittest
from pg2536_strict_normal_publication_post import W, compose


class CurrentSchemaPost(unittest.TestCase):
    def setUp(self):
        path = W / 'pg2514-current-cdbc-before-v2/payload.private.py'
        self.raw = path.read_text()
        self.receipt = json.loads((path.parent / 'manifest.safe.json').read_bytes())

    def test_actual_reader_whole_phases_ten_fields_and_separate_native(self):
        raw = compose(self.raw, self.receipt, {'actualExit':0, 'fileHashes':{}}, 'a'*64)
        for marker in ["require('native' not in after and 'native' not in old_after)",
                       'require(json.loads(pub_before)==old_after)', 'native==json.loads',
                       'len(phases)>=7', "for stamp,phase,observed in phases:oracle['verify']",
                       "str(base / 'pg2512-manifest.sig')", 'pg2535-strict-normal-publication-v1',
                       '/opt/schubert-nk/releases/0.1.0-PG2512', "'unitExchangeAndReload':False"]:
            self.assertIn(marker, raw)
        self.assertNotIn("old_after['native']", raw)
        self.assertNotIn("set(old_after)-{'native'}", raw)
        self.assertEqual(self.receipt['payloadSha256'], hashlib.sha256(self.raw.encode()).hexdigest())

    def test_wrong_source_schema_hash_boolean_and_bom_are_refused(self):
        for key, value in [('actualExit',False), ('productionSource','old'), ('privateBeforeSha256','wrong'), ('payloadSha256','wrong')]:
            with self.assertRaises(ValueError):
                compose(self.raw, {**self.receipt,key:value}, {'actualExit':0,'fileHashes':{}}, 'a'*64)
        for value in [None, 'x'*64, 'a'*63]:
            with self.assertRaises(ValueError):
                compose(self.raw, self.receipt, {'actualExit':0,'fileHashes':{}}, value)


if __name__ == '__main__':
    unittest.main()
