"""Actual standalone stage positive source/BOM and new archive namespaces, foreign vectors."""
import ast
import unittest
from pyflakes.api import check
from pg2038_fresh_current_stage_owned_stop_dispatch import STAGE,ARCHIVE


class Stage(unittest.TestCase):
    def test_actual_current_guard_and_new_slots(self):
        self.assertEqual(0,check('DIGEST="fixed"\nFILES={}\n'+STAGE,'<actual standalone current stage>'))
        self.assertTrue('PG1638'not in STAGE);self.assertTrue('pg2038-fixed-stage-v1'in STAGE);self.assertTrue(ARCHIVE in STAGE)
        node=next(n for n in ast.parse(STAGE).body if isinstance(n,ast.Assert)and 'json.loads(manifest)'in ast.get_source_segment(STAGE,n))
        code=compile(ast.Expression(node.test),'<actual current BOM/source predicate>','eval')
        class Hash:
            def __init__(self,digest):self.digest=digest
            def sha256(self,data):return self
            def hexdigest(self):return self.digest
        class Json:
            def __init__(self,source):self.source=source
            def loads(self,data):return {'source':{'commit':self.source}}
        for digest,source,wanted in [('ee75d0cd61457462eca59e67f5af2d8e677427071514940f3fb594ba93a026d7','0fd734195b4d5338f6b7e860e087cce561d49562',True),('foreign','0fd734195b4d5338f6b7e860e087cce561d49562',False),('ee75d0cd61457462eca59e67f5af2d8e677427071514940f3fb594ba93a026d7','foreign',False)]:
            self.assertEqual(wanted,eval(code,{'hashlib':Hash(digest),'json':Json(source),'manifest':b'literal'}))


if __name__=='__main__':unittest.main()
