"""Current point-window/immutable before archive bindings, not historical source input."""
import json
import unittest
from pg1446_current_cold_stage import W
from pg2382_current_resume_native_catalog import catalog_source,SOURCE,TOOLS


class CurrentNative(unittest.TestCase):
    def test_actual_catalog_root_window_and_preserved_before_ten(self):
        v=json.loads((W/'pg2362-current-resume-live-binding-v1/manifest.safe.json').read_bytes())
        t=json.loads((W/'pg2364-current-resume-terminal-v1/manifest.safe.json').read_bytes())
        receipt=(W/TOOLS/'pg2374_parent_receipt.py').read_text()
        raw=catalog_source(receipt,v['binding'],t['endMonotonicUs'])
        self.assertTrue(raw.startswith(receipt+'\n'))
        self.assertIn('native-before-private',raw);self.assertIn('require(len(old)==10)',raw)
        self.assertIn("snapshot['before']==frozen",raw)
        self.assertIn('relative not in old or old[relative]',raw)
        self.assertIn('priorSameSourcePointsImported',raw)
        self.assertNotIn('ordinaryNoargs',raw);self.assertNotIn('pg2227-newboot',raw)
        self.assertNotIn('pg2246',raw);self.assertIn(SOURCE,raw)
        self.assertIn("binding.get('activation') != '9be93262-fbb2-438f-b2b0-c4a27f5563a4'",raw)


if __name__=='__main__':unittest.main()
