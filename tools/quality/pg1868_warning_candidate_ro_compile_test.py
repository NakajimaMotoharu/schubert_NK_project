"""Direct source qualification without old nested namespace admissions."""
import inspect
import unittest
from pg1868_warning_candidate_ro_compile import main


class Direct(unittest.TestCase):
    def test_actual_direct_body_whole_python_java_and_old_new_inputs(self):
        raw=inspect.getsource(main)
        for v in ['pg1866-warning-unused-independent-post-v1','pg1861-frozen-v1.safe.json','pg1860-warning-unused-tools-v1','inventory(TARGET)','check(raw','Pg1867OriginalTupleTest','Pg1867CurrentIdentityTest','Pg1867InputBoundaryTest','pg1638-release-v1']:
            self.assertIn(v,raw)
        self.assertNotIn('namespace(candidate)',raw)


if __name__=='__main__':unittest.main()
