"""Independent graph namespace/receipt negatives; no owner actions or candidate publication."""
import json
import unittest
from pg1446_current_cold_stage import W
import pg2374_current_resume_owned_sources as p


class CurrentGraph(unittest.TestCase):
    def test_current_whole_graph_and_receipt_not_rebound_as_positive(self):
        ctx=p.previous.context()
        live=json.loads((W/'pg2362-current-resume-live-binding-v1/manifest.safe.json').read_bytes())
        state=json.loads((W/'pg2234-newboot-fresh-day-terminal-v1/manifest.safe.json').read_bytes())['parentState']
        graph=p.emit(ctx,live,state,{})
        self.assertEqual(15,len(graph))
        receipt=graph['pg2374_parent_receipt.py']
        self.assertIn("binding.get('activation') != '9be93262-fbb2-438f-b2b0-c4a27f5563a4'",receipt)
        self.assertIn(live['binding']['activation'],receipt)
        body='\n'.join(v for n,v in graph.items()if n not in {'pg2374_parent_receipt.py','pg2374_warning_parent_projection.py'})
        for value in ['pg2368-current-resume-full-seal-v1',p.TOOLS,'0.1.0-PG2126','Pg387TrustedDeployment.STEM="pg2126"']:self.assertIn(value,body)
        self.assertNotIn('pg2274',body);self.assertNotIn('Pg2274',body)
        self.assertNotIn('pg1846',body)


if __name__=='__main__':unittest.main()
