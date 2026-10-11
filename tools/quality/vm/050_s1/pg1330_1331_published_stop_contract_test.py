import ast
import unittest
from pg1330_published_owned_stop_preflight import payload
from pg1331_published_owned_stop_dispatch import source,STAGE
from pg1328_published_owned_stop_sources import BEFORE,SOURCE


class PublishedStopDispatchTest(unittest.TestCase):
    def test_actual_fullpreflight_and_reserved_stage_stop_names(self):
        pre=payload();code=source();compile(pre,'<fullpreflight>','exec');compile(STAGE,'<actual stage>','exec')
        self.assertIn(BEFORE,pre);self.assertIn('current==json.loads(sealed_current)',pre)
        self.assertIn('pg1330-published-stop-preflight-v1.safe.json',code)
        self.assertIn('pg1329-frozen-v1.safe.json',code)
        self.assertIn('Pg1328OriginalTupleTest',code)
        self.assertIn('0.1.0-PG1292',code)
        self.assertLess(code.index("+'.requested').open('x')"),code.index("if action=='stage':"))
        main=ast.parse(code).body[0]
        test=next(n.test for n in main.body if isinstance(n,ast.If)and 'genuineParentBeforeSha256'in ast.unparse(n.test))
        env={'frozen':{'actualExit':0,'productionSource':SOURCE,'genuineParentBeforeSha256':BEFORE},'pre':{'actualExit':0,'privateBeforeSha256':BEFORE},'SOURCE':SOURCE,'BEFORE':BEFORE}
        self.assertFalse(eval(compile(ast.Expression(test),'<actual full precondition>','eval'),env))
        for key,bad in [('actualExit',1),('privateBeforeSha256','0'*64)]:
            env['pre'][key]=bad
            self.assertTrue(eval(compile(ast.Expression(test),'<actual full precondition>','eval'),env));env['pre'][key]=0 if key=='actualExit'else BEFORE

if __name__=='__main__':unittest.main()
