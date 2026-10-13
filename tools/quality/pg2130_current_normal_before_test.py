import json
import unittest
from pg1446_current_cold_stage import W
import pg2096_current_newrun_terminal_post as prior
from pg2130_current_normal_before import payload,entry,SLOT

class CurrentBefore(unittest.TestCase):
    def test_exact_current_payload_and_isolated_entry(self):
        post=json.loads((W/'pg2096-current-newrun-terminal-post-v1/manifest.safe.json').read_bytes())
        seals={k:post['proofHashes'][k]['sha256']for k in prior.previous.SEALS}
        raw=payload(seals)
        # Identity comes from the separately hashed current receipt, not a duplicate inline UUID.
        self.assertIn("root = base / 'pg2090-native-stop-v1'",raw)
        for value in seals.values():self.assertIn(value,raw)
        self.assertIn("'before.private.json',actual",raw)
        self.assertIn("'allTenUnitsKernelEmpty':True",raw)
        self.assertIn("'pg2130-current-normal-before-v1'",raw)
        self.assertNotIn("'run': 'PG2040",raw)
        old=prior.SLOT;fn=entry()
        self.assertEqual(old,prior.SLOT)
        self.assertEqual(SLOT,fn.__globals__['SLOT'])
        self.assertIs(payload,fn.__globals__['payload'])
        self.assertEqual('pg2090-current-newrun-owned-stop-tools-v1',fn.__globals__['TOOLS'])

if __name__=='__main__':unittest.main()
