"""Actual generated noargs source/guard/observer/data identity, no external start."""
import ast,unittest
from pg956_current_observer import source as observer
from pg957_current_once import payload
class Test(unittest.TestCase):
    def test_one_guard_before_one_start_and_actual_current_hash(self):
        raw=payload();ast.parse(raw)
        for s in ('72d51bd2b7db519b89160881b6b6a1322ee4d8ef68d94bc6b23e6c9724cdb3aa','40ef6e894573d2ffab1d1732124960f9c98d5f97','b75e8bd539edf40d1324896a16e51842d00a3983ba1eae661c86ab68d4692524','pg957-ordinary-once-v1',"'attemptReserved':True,'repeatForbidden':True",'originalBudgetSeconds',"assert before['ordinaryNoargs']",'standard_snapshot(limited)==before==standard_snapshot(protected())'):
            self.assertIn(s,raw)
        self.assertEqual(1,raw.count("subprocess.run(['/usr/bin/systemctl','start'"))
        self.assertLess(raw.index("persist('external-start-guard.private.json'"),raw.index("subprocess.run(['/usr/bin/systemctl','start'"))
        self.assertIn("os.fsync(fd)",raw)
        marker="before_raw=pathlib.Path('/var/lib/pgpt-s1-preservation/pg954-ordinary-before-v1/after.private.json')"
        self.assertEqual(1,raw.count(marker));self.assertGreater(raw.index(marker),raw.index('before_raw=before_path.read_bytes()'))
        operation=raw[raw.index(marker):]
        self.assertIn('pg954-ordinary-before-v1',operation);self.assertIn('pg957-ordinary-once-v1',operation)
        self.assertNotIn('pg872-ordinary-once',raw);self.assertNotIn('pg870-ordinary-before',operation)
    def test_observer_is_new_source_and_cannot_issue(self):
        raw=observer();ast.parse(raw)
        for s in ('pg956','PG932','pg954-ordinary-before-v1','40ef6e894573d2ffab1d1732124960f9c98d5f97','b75e8bd539edf40d1324896a16e51842d00a3983ba1eae661c86ab68d4692524'):
            self.assertIn(s,raw)
        self.assertNotIn('PG862',raw);self.assertNotIn('pg871',raw);self.assertNotIn('StartUnit',raw)
if __name__=='__main__':unittest.main()
