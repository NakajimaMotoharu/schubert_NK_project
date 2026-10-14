import ast
import json
import unittest
from pyflakes.api import check
import pg1257_fresh_independent_terminal_post as schema
from pg1446_current_cold_stage import W
from pg2656_current_a79_before import payload, SLOT


class CurrentA79Before(unittest.TestCase):
    def test_current_actual_before_preserves_all_fields_and_no_business_action(self):
        receipt=json.loads((W/'pg2560-strict-current-owned-post-v1/manifest.safe.json').read_bytes())
        seals={n:receipt['proofHashes'][n]['sha256']for n in schema.previous.SEALS}
        raw=payload(seals);self.assertEqual(0,check('HASHES={}\nRECEIPT="actual"\n'+raw,'<before whole namespace>'))
        for marker in [SLOT,'b29fb3e5-2c46-4eac-b8f3-d03b986338e3','a79b45b5858a186fa82bec1ff36882271ab996a4','flat=validate_current_image(after,native)']:
            self.assertIn(marker,raw)
        self.assertNotIn("require(after['native']==native)",raw)
        forbidden={'start','stop','restart','reload','daemon-reload','reset-failed'}
        for n in ast.walk(ast.parse(raw)):
            if isinstance(n,ast.List):self.assertFalse(forbidden&{v.value for v in n.elts if isinstance(v,ast.Constant)and isinstance(v.value,str)})

    def test_missing_seals_refused_before_guest(self):
        with self.assertRaises(ValueError):payload({})


if __name__=='__main__':unittest.main()
