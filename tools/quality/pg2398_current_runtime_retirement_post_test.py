import json
import unittest
from pyflakes.api import check
from pg1446_current_cold_stage import W
import pg1257_fresh_independent_terminal_post as schema
from pg2398_current_runtime_retirement_post import payload,BASE,SHA


class Post(unittest.TestCase):
    def test_whole_observer_exact_delta_and_original_dialect(self):
        p=json.loads((W/'pg2380-current-resume-owned-post-v1/manifest.safe.json').read_bytes());seals={n:p['proofHashes'][n]['sha256']for n in schema.previous.SEALS}
        s=payload(seals);self.assertEqual(0,check('HASHES={}\nRECEIPT="actual"\n'+s,'<current independent retirement post>'))
        for x in [BASE,SHA,'same_except_runtime','prior_equal','exactRuntimeEntryRetired','pg2392-native-stop-v1','runtimeRetiredOnly=true']:self.assertIn(x,s)
        self.assertIn("'ownedExplicitStops': 0",s)
        self.assertNotIn('pg2050',s)


if __name__=='__main__':unittest.main()
