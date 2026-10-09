"""Independent phase/source/baseline/directory/whole bundle guard before compile or VM."""
import ast
import unittest
from pathlib import Path
import pg835_pending_sources as p
class Test(unittest.TestCase):
    def test_direct_entrypoints_are_unique_before_any_dispatch(self):
        directory=Path(__file__).resolve().parent
        for name in ('pg835_pending_native.py','pg835_candidate_place.py','pg835_pending_compile.py'):
            tree=ast.parse((directory/name).read_text())
            mains=[n for n in tree.body if isinstance(n,ast.If)and '__name__'in ast.unparse(n.test)]
            self.assertEqual(1,len(mains),name)
    def test_before_after_sources_and_full_current_baseline(self):
        java=p.java();snapshot=p.snapshot_library();refs=p.refs();guard=p.before_freeze()
        for raw in (snapshot,refs,guard):ast.parse(raw)
        self.assertIn('Pg835PendingDeployment',java)
        self.assertIn('args[0].equals("2a0d5aa392c85a1dc12a1cdb423978e8500895b8")',java)
        self.assertIn('0.1.0-PG832',java);self.assertIn('0.1.0-PG796',java)
        self.assertIn('pg833-current-before832-v1/after.private.json',snapshot)
        self.assertIn(p.BASELINE,snapshot);self.assertIn("==554",snapshot)
        self.assertIn("{k:value[k]for k in ('rows','trees','configuration')}",snapshot)
        self.assertIn('/releases/0.1.0-PG796',snapshot)
        self.assertIn('/releases/0.1.0-PG832',refs)
        self.assertIn('/releases/0.1.0-PG796',guard)
        self.assertIn("if phase in(b'after',b'release'):h.parent=after_parent",refs)
        for raw in (java,snapshot,refs,guard):
            self.assertNotIn('PG750',raw);self.assertNotIn('pg800-probe-post',raw)
            self.assertNotIn('NEXT_',raw);self.assertNotIn('2797579',raw)
        self.assertIn('epochUnchanged=true',java);self.assertIn('databaseUpdates0=true',java)
if __name__=='__main__':unittest.main()
