"""Whole reuse qualification and explicit no new dependency exit vs actual target exit."""
import unittest
import pg1409_batch_qualified_dependency_selected_v4 as p

class Test(unittest.TestCase):
    def test_actual_complete_dependency_and_target_scope(self):
        raw=p.source()
        for s in ('pg1408-batch-boundary-selected-v1/manifest.safe.json',"'dependencyBuildExit':None",'dependencyNotReissued','dependencyMainClassBytesEqual1279','len(dependency_same)==3','fresh_xml(p,suite','pg1409-batch-boundary-selected-v1'):
            self.assertIn(s,raw)
        self.assertNotIn('subprocess.run(dependency_args',raw)
        self.assertIn('subprocess.run(args,cwd=T',raw)
        compile(raw,'<actual qualified dependency reuse>','exec')

if __name__=='__main__':unittest.main()
