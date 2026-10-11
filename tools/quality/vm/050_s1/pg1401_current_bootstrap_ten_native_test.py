"""Whole native source/run/session/host qualification, not coverage artificial calls."""
import ast
import unittest
import pg1401_current_bootstrap_ten_native as p

class Test(unittest.TestCase):
    def test_actual_whole_same_source_binding(self):
        raw=p.source()
        for s in ('769ddb15cd735c25fef581b5f9850ef9d0053c0f','pg1400-existing-admin-independent-post-v1','PG1400-existing-admin-independent-post-v1','pg1396-bootstrap-existing-v3','pg1341-published-eight-native-v1','pg1279-held-channel-six-host-v1',"h['tests']==3569",'classByteMismatch',"new_sessions[0]['sessionIdSha256']==new_sessions[1]['sessionIdSha256']","'otherSourceNativeImported':0"):
            self.assertIn(s,raw)
        for old in ('40ef6e894573d2ffab1d1732124960f9c98d5f97','pg983','pg972','pg926','pg992-current-ten-native-v1'):
            self.assertNotIn(old,raw)
        ast.parse(raw)

if __name__=='__main__':unittest.main()
