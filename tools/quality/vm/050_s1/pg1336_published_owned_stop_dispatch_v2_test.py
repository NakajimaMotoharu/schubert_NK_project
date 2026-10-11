import unittest
from pg1336_published_owned_stop_dispatch_v2 import source,STAGE,GUEST

class CurrentWholeStageBindingTest(unittest.TestCase):
    def test_sent_stage_current_and_main_abi_namespace_consistency(self):
        code=source();compile(code,'<actual main>','exec');compile(STAGE,'<actual sent stage>','exec')
        for text in [code,STAGE]:
            self.assertTrue('PG1068'not in text)
            self.assertTrue('pg1328'not in text)
            self.assertTrue('pg1331'not in text)
            self.assertTrue('0.1.0-PG1292'in text)
        self.assertIn('pg1334-native-tools-v1',GUEST)
        self.assertIn('pg1335-frozen-v1.safe.json',code)
        self.assertIn('pg1338-published-stop-preflight-v2.safe.json',code)
        self.assertIn('Pg1334OriginalTupleTest',code)
        self.assertLess(code.index("pg1336-stage-v1.exit"),code.index('prefix='))
        self.assertIn("!=b'0\\n'",code)

if __name__=='__main__':unittest.main()
