"""Independent existing runtime golden and actual profile/bundle no-start closure."""
import ast,unittest
import pg860_retirement as p
class Test(unittest.TestCase):
    def test_fixed_existing_runtime_bytes(self):
        import pg815_retirement_test as old
        old.Test('test_actual_runtime_derive_fixed_literal').test_actual_runtime_derive_fixed_literal()
    def test_actual_full_profile_closure(self):
        expected='ba0ec596c2800f4403f04c545869e2bbe500bd14c6706e4dc2ae4fa9c1a5b2fd'
        self.assertEqual(expected,p.SNAPSHOT)
        raw=p.bind(p.compiler.source()).replace('import pg860_retirement_sources as p','import pg860_retirement as p')
        ast.parse(raw);self.assertIn('pg860_retirement_test.py',raw);self.assertIn('pg859-completed-failed-post-v1',raw)
        native=p.native_source();ast.parse(native)
        self.assertIn('pg860-retirement-tools-v1',native)
        self.assertIn('Pg860RuntimeRetirement retire',native)
        self.assertIn('0.1.0-PG832',native)
        self.assertNotIn('0.1.0-PG796',native)
        s=p.snapshot_library();self.assertIn(expected,s);self.assertIn("fields['epoch_id']=='8b153538-1523-4987-a456-6cbea0d345ee'",s)
        self.assertNotIn("fields['epoch_id']=='0eece14c-f832-47c2-b7dd-14125682e7ea'",s)
        for name,value in p.sources().items():
            if name.endswith('.py'):ast.parse(value)
        j=p.java();self.assertIn('runtime.unlinkEntry("pg841-once-resume.conf")',j)
        self.assertIn('lease.confirmClosed()',j);self.assertIn('originalCompletedUnchanged',j)
        self.assertNotIn('RuntimeResume',j)
        for r in (p.helper(),s):
            self.assertNotIn('stop_one',r);self.assertNotIn("'stop',",r);self.assertNotIn("'start',",r)
            self.assertNotIn('pg805-once-resume.conf',r)
if __name__=='__main__':unittest.main()
