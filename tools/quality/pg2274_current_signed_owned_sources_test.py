"""Independent whole graph generation and signature-path regression oracle."""
import unittest
import pg2274_current_signed_owned_sources as graph
import pg2276_current_signed_owned_dispatch as dispatch
import pg2280_current_signed_owned_post as post
import pg2282_current_signed_native_catalog as catalog
import pg2284_current_signed_native_qualification as qualification
from pg2208_current_newboot_cold_sources import BOOT
from pyflakes.api import check


class SignedCurrentGraph(unittest.TestCase):
    def test_all_generation_fields_and_actual_manifest_stem(self):
        generated=graph.sources();self.assertGreaterEqual(len(generated),15)
        raw=generated['Pg2274NativeStop.java']
        for value in ['LABEL="PG2126"','STEM="pg2126"','0.1.0-PG2126',graph.SOURCE,graph.BOM,'expectedSqlCount=28',BOOT,'91f5484b-9702-4c7c-97f3-dd5110a853f9']:
            self.assertIn(value,raw)
        self.assertNotIn('STEM="pg1846"',raw)
        self.assertNotIn('pg2246',raw)
        for name,body in generated.items():
            self.assertNotIn('2246',name)
            if name.endswith('.py'):self.assertEqual(0,check(body,'<whole signed-current fixture>'))

    def test_current_boot_archive_stage_dispatch_and_new_once_slots(self):
        self.assertIn(BOOT,dispatch.STAGE)
        self.assertNotIn('3d69f5af',dispatch.STAGE)
        self.assertIn(dispatch.ARCHIVE,dispatch.STAGE)
        self.assertIn(graph.TOOLS,dispatch.STAGE)
        raw=dispatch.run_source();compile(raw,'<actual corrected once dispatch>','exec')
        for value in ['pg2275','pg2276','pg2277','pg2278','Pg2274']:self.assertIn(value,raw)
        for old in ['pg2266','pg2247','pg2249','pg2250','Pg2246']:self.assertNotIn(old,raw)

    def test_whole_post_and_catalog_corrected_receipt_chain(self):
        import json
        from pg1446_current_cold_stage import W
        seals={k:'a'*64 for k in post.prior.prior.prior.previous.SEALS}
        raw=post.payload(seals);self.assertEqual(0,check('HASHES={}\nRECEIPT="fixture"\n'+raw,'<corrected full post>'))
        self.assertIn('pg2274-native-stop-v1',raw)
        self.assertIn(graph.TOOLS,raw)
        self.assertNotIn('pg2274-newboot-owned-stop-tools-v1',raw)
        self.assertIn('PG2281-current-signed-owned-post-v2',raw)
        self.assertNotIn('pg2246',raw)
        live=json.loads((W/'pg2230-newboot-current-live-binding-v1/manifest.safe.json').read_bytes())
        end=json.loads((W/'pg2234-newboot-fresh-day-terminal-v1/manifest.safe.json').read_bytes())['endMonotonicUs']
        raw=catalog.catalog_source(graph.sources()['pg2274_parent_receipt.py'],live['binding'],end)
        self.assertEqual(0,check('SEALS={}\n'+raw,'<corrected catalog>'))
        self.assertIn('pg2274-native-stop-v1',raw)
        self.assertEqual('pg2274-current-signed-owned-stop-tools-v1',catalog.TOOLS)
        self.assertNotIn('pg2274-newboot-owned-stop-tools-v1',raw)
        self.assertNotIn('pg2246',raw)
        self.assertIn('streams=[p for i,p in enumerate(streams)if i!=early_index]',qualification.prior.server())
        self.assertIn("len(streams)==9",qualification.prior.server())


if __name__=='__main__':unittest.main()
