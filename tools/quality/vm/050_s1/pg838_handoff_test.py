import ast
import unittest
from pg838_reference_handoff import payload
class Test(unittest.TestCase):
    def test_exact_two_actors_beforepublication_no_business_operations(self):
        raw=payload();ast.parse(raw)
        for value in ('3413229,16968012','3413338,16968640','pg835-pending-tools-v2',
                      'knownBeforePublicationJavaAndRefGone=true','signal.SIGTERM',
                      'refs-before.private.json',"[b'1',b'1']if expect_owned else[b'0',b'0']"):
            self.assertIn(value,raw)
        for value in ('SIGKILL','systemctl start','systemctl stop','3412116','16855351'):
            self.assertNotIn(value,raw)
if __name__=='__main__':unittest.main()
