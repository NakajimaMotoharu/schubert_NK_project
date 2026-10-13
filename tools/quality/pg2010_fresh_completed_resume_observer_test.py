"""Actual observer source, immutable three-file namespace and original budget contract."""
import ast
import unittest
from pyflakes.api import check
from pg2010_fresh_completed_resume_observer import namespace,source


class Observer(unittest.TestCase):
    def test_actual_whole_source_closure_no_start_stop(self):
        raw=source();self.assertEqual(0,check(raw,'<actual observer driver>'))
        ns=namespace();files=ns['files']();self.assertEqual({'pg2010_watch_parent.py','pg457_stable_actor.py','pg462_observer_identity.py'},set(files))
        for name,body in files.items():self.assertEqual(0,check(body,'<actual '+name+'>'))
        watch=files['pg2010_watch_parent.py']
        self.assertTrue('PG1846' in watch);self.assertTrue('3d69f5af-6bac-46b1-a540-7591c4a79a0d' in watch)
        self.assertTrue("deadline=int(m['ExecMainStartTimestampMonotonic'])/1e6+1860" in watch)
        self.assertTrue('pg2006-existing-runtime-independent-post-v1/manifest.safe.json' in raw)
        for node in ast.walk(ast.parse(watch)):
            if isinstance(node,ast.List):
                values=[n.value for n in node.elts if isinstance(n,ast.Constant)]
                self.assertFalse(any(v in values for v in ['start','stop','restart','reload','daemon-reload']))


if __name__=='__main__':unittest.main()
