"""Actual new source/case/clock/gates; no VM or Current oracle changes."""
import ast,unittest
from pg960_current_genuine import payload,source
from pg961_current_a01 import code
class Test(unittest.TestCase):
    def test_genuine_new_tuple_and_original_budget(self):
        p=payload();s=source();ast.parse(p);ast.parse(s)
        for v in ('eeae04ea-713c-4f2d-888d-358fb4bed274','2026-10-09T23:31:22.087768Z','091663ce-1cf4-47e7-8311-218ebb0c8653','3844442','0bb4d6f3b9e74cdc91c553748a4cd018','213904','201380374989','40ef6e894573d2ffab1d1732124960f9c98d5f97','b75e8bd539edf40d1324896a16e51842d00a3983ba1eae661c86ab68d4692524','pg957-ordinary-once-v1','pg954-ordinary-before-v1','==584'):
            self.assertIn(v,p)
        self.assertIn('pg956-watch-v1.exit',s);self.assertIn('pg961-chr-a01-native-v1.exit',s)
        self.assertIn("observed['terminalObserved']",s);self.assertIn("observed['parentExit']=='0'",s)
        self.assertNotIn('pg875-',p);self.assertNotIn('pg885-',p)
    def test_chr_exact_current_not_old_result(self):
        p=code();ast.parse(p)
        for v in ('PG961','pg956','pg957-ordinary-once-v1','pg954-ordinary-before-v1','40ef6e894573d2ffab1d1732124960f9c98d5f97','b75e8bd539edf40d1324896a16e51842d00a3983ba1eae661c86ab68d4692524'):
            self.assertIn(v,p)
        self.assertNotIn('pg876-',p);self.assertNotIn('pg849-',p)
if __name__=='__main__':unittest.main()
