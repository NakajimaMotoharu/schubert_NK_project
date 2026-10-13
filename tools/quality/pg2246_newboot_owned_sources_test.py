import json
import unittest
from pyflakes.api import check
from pg1446_current_cold_stage import W
from pg2208_current_newboot_cold_sources import BOOT
import pg2246_newboot_owned_sources as p


class CurrentOwnedGraph(unittest.TestCase):
    def test_whole_real_graph_body_newboot_and_receipt_negatives(self):
        old=p.prior.context();live=json.loads((W/'pg2180-newsource-live-binding-v1/manifest.safe.json').read_bytes())
        state=json.loads((W/'pg2182-newsource-terminal-receipt-v1/manifest.safe.json').read_bytes())['parentState']
        binding={**live['binding'],'boot':BOOT.replace('-',''),'run':'11111111-1111-4111-8111-111111111111','activation':'22222222-2222-4222-8222-222222222222','cutoff':'2026-10-13T15:01:00Z'}
        new_live={**live,'binding':binding}
        graph=p.emit_sources(old,new_live,state,{})
        self.assertGreaterEqual(len(graph),15)
        for name,raw in graph.items():
            self.assertNotIn('2188',name)
            if name.endswith('.py'):self.assertEqual(0,check(raw,'<whole actual owned fixture>'))
        receipt=graph['pg2246_parent_receipt.py'];self.assertIn('02bddddf-9cd3-4668-9d67-7561232fc4e4',receipt)
        body='\n'.join(v for n,v in graph.items()if n!='pg2246_parent_receipt.py')
        self.assertIn(BOOT,body);self.assertNotIn('3d69f5af',body)
        self.assertIn('pg2242-newboot-fresh-day-full-seal-v1',body)
        self.assertIn(p.TOOLS,body)
        self.assertNotIn('pg2246-newsource-owned-stop-tools-v1',body)
        self.assertIn('0.1.0-PG2126',body)
        self.assertNotIn('pg2188',body)


if __name__=='__main__':unittest.main()
