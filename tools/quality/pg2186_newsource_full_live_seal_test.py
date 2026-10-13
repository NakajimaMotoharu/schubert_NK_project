import json
import unittest
from pg1446_current_cold_stage import W
import pg2186_newsource_full_live_seal as p


class FullSeal(unittest.TestCase):
    def test_actual_current_source_run_native_before_and_guard(self):
        live=json.loads((W/'pg2180-newsource-live-binding-v1/manifest.safe.json').read_bytes())
        raw=p.payload({**live['binding'],'rootPid':live['rootPid']})
        for text in ['3b7f3567b54f91f3a9dbeb859e8dd77e8353a2c8','62213f357c9dab3b00b557549426b091a03ace6557a62f4410999a02028a332c','0.1.0-PG2126','pg2178-newsource-noargs-once-v1',p.BEFORE,'02bddddf-9cd3-4668-9d67-7561232fc4e4','20b86040-ffd5-4d17-9fca-5d83048ba905','before_shape(before)']:self.assertIn(text,raw)
        self.assertNotIn('796965f389b631bf8abb49f6cbccf88955fbf3afe39edec0194316df35248a05',raw)
        self.assertNotIn('0.1.0-PG1846',raw)
        self.assertEqual(p.entry().__globals__['SOURCE'],p.SOURCE)


if __name__=='__main__':unittest.main()
