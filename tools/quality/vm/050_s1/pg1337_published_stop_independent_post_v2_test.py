import unittest
from pg1337_published_stop_independent_post_v2 import payload

class CorrectedNormalStopPostTest(unittest.TestCase):
    def test_complete_current_namespace_source_and_genuine_root(self):
        v={n:'a'*64 for n in ['before.private.json','after.private.json','complete.private','parent.private.jsonl']}
        code=payload(v);compile(code,'<actual current newpost>','exec')
        for part in ['pg1334-native-tools-v1','pg1334-native-stop-v1','0.1.0-PG1292','75132489604','normalCurrentOwnedStopScopesSealed','len(rows)==24','manager.UnrefUnit']:
            self.assertTrue(part in code,part)
        for part in ['pg1328','PG1068','normalPG877NewScopesSealed','580631']:
            self.assertTrue(part not in code,part)

if __name__=='__main__':unittest.main()
