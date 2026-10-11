import unittest
from pg1340_published_stop_independent_post_v4 import payload,source

class CurrentPublicRunIdentityTest(unittest.TestCase):
    def test_actual_full_payload_public_run_matches_actual_host_slot(self):
        values={n:'a'*64 for n in ['before.private.json','after.private.json','complete.private','parent.private.jsonl']}
        code=payload(values)
        self.assertEqual(code.count("'run':'PG1340-published-terminal-post-v4'"),1)
        self.assertIn("base=W/'pg1340-published-terminal-post-v4'",source())
        for old in ['PG1332-published-terminal-post-v1','pg1332','pg1337','PG1257']:
            self.assertTrue(old not in code,old)
        self.assertIn('normalCurrentOwnedStopScopesSealed',code)

if __name__=='__main__':unittest.main()
