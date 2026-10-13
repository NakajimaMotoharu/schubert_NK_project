import json
import unittest
from pyflakes.api import check
from pg1446_current_cold_stage import W
from pg2208_current_newboot_cold_sources import BOOT
import pg2252_newboot_owned_post as p


class IndependentCurrentPost(unittest.TestCase):
    def test_whole_exported_current_post_without_an_old_stop(self):
        seals={k:'a'*64 for k in p.prior.prior.previous.SEALS}
        live=json.loads((W/'pg2180-newsource-live-binding-v1/manifest.safe.json').read_bytes())
        live['binding']={**live['binding'],'boot':BOOT.replace('-',''),'run':'11111111-1111-4111-8111-111111111111','activation':'22222222-2222-4222-8222-222222222222','cutoff':'2026-10-13T15:01:00Z'}
        raw=p.emit_payload(seals,p.prior.context(),live)
        self.assertEqual(0,check('HASHES={}\nRECEIPT="actual"\n'+raw,'<whole actual post>'))
        for value in [p.SLOT,p.TOOLS,'pg2246-native-stop-v1','all24UnchangedTwice','PG2252-newboot-owned-stop-post-v1',BOOT]:self.assertIn(value,raw)
        self.assertNotIn('pg2188',raw)
        self.assertNotIn('3d69f5af',raw)
        self.assertEqual(p.SLOT,p.entry().__globals__['SLOT'])


if __name__=='__main__':unittest.main()
