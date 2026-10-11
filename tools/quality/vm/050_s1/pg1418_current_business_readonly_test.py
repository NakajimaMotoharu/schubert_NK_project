"""Qualify actual generated graph before any SSH dispatch."""
import ast
import json
import unittest
import pg1418_current_business_readonly as p
import pg1220_current_full32_terminal_post as t

class Test(unittest.TestCase):
    def test_current_before_native_backup_log_scope_and_normal_close(self):
        v=json.loads((p.W/'pg1340-published-terminal-post-v4.safe.json').read_bytes())
        raw=p.payload({k:v['proofHashes'][k]['sha256']for k in t.SEALS})
        tree=ast.parse(raw)
        scopes=[n for n in tree.body if isinstance(n,ast.Try)and 'manager.RefUnit' in ast.unparse(n)]
        self.assertEqual(1,len(scopes))
        scope=ast.unparse(scopes[0])
        for expected in ('observe_backup()', 'verify_fresh(', 'manager.UnrefUnit', 'keys', 'key[:]'):
            self.assertIn(expected,scope)
        for expected in (p.SOURCE,p.RUN,p.CUT,p.BEFORE,p.SLOT,'588c880aed434af6a6bb89c7ad3bf076','CONFIG_SOURCE','BEFORE_RECEIPT','causalLog','ordinaryBackupPgRestoreListExit'):
            self.assertIn(expected,raw)
        self.assertNotIn('pg1238-fresh-day-ordinary-before-v1',raw)
        self.assertNotIn('4236e5a9bfd94fe09ca34323687bc5c3',raw)
        self.assertNotIn('PG1266-fresh-independent-log-v1',raw)
        self.assertIn('externalFixtureRequestCountKnown',raw)
        self.assertIn('qa051FinalPass',raw)
        compile(raw,'<full current readonly graph>','exec')

if __name__=='__main__':unittest.main()
