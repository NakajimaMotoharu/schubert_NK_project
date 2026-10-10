import unittest
import pg1236_completed_runtime_retired_post as p

class PostTest(unittest.TestCase):
    def test_whole_payload_current_new_scope_and_independent_before_join(self):
        s=p.payload();compile(s,'<actual independent finite delta>','exec')
        for part in ['retirement.same_except_runtime(before,after',"before.items()if k!='native'",'21505d35e87a01314e63a2b834d1570d0d96a4b02a5fe9af4c117c35c7867c36',"'ownedExplicitStops':0",'runtimeRetiredOnly=true',"'run':'PG1236-completed-runtime-retired-post-v1'", "'oldFailedScopeNormalClose':False"]:
            self.assertTrue(part in s,part)
        self.assertFalse('pg1216-native-tools-v1'in s)
        self.assertFalse("'run':'PG1220-terminal-final-v1'"in s)
        for k,v in p.SEALS.items():self.assertTrue(v in s,k)

if __name__=='__main__':unittest.main()
