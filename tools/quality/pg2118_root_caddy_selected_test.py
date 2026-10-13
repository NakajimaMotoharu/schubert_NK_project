import unittest
from pyflakes.api import check
from pg2118_root_caddy_selected import server

class Selection(unittest.TestCase):
    def test_complete_six_suite_literal_and_real_exports(self):
        raw=server()
        self.assertEqual(0,check('HEAD="fixed"\nARCHIVE_SHA="fixed"\n'+raw,'<actual Root Caddy selection>'))
        self.assertIn('RootGenerationTruthTableTest,RootStartupContextTest',raw)
        self.assertIn("'tests':1,'failures':0,'errors':0,'skipped':0",raw)
        self.assertIn("'tests':4,'failures':0,'errors':0,'skipped':0",raw)
        self.assertNotIn('PG2116',raw)
        self.assertNotIn('-DskipTests',raw)
        self.assertNotIn('-DfailIfNoTests=false',raw)

if __name__=='__main__':unittest.main()
