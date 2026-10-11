import ast
import unittest
from pg1458_current_day_done import compose


class DoneSourceTest(unittest.TestCase):
    def fixture(self):return {'boot':'3d69f5af6bac46b1a5407591c4a79a0d','invocation':'1ee3b3e121c74e63ae28fe4d912e9ede','job':'13033','start':5711141318,'run':'15700a87-9117-4f63-a0ff-768dd604d0f1','cutoff':'2026-10-11T21:18:59.040097Z','activation':'9e706936-a3c9-4a09-bb66-e2b1e8bbef66'}
    def test_actual_capture_is_bound_not_old_success(self):
        t=ast.parse(compose(self.fixture()));assign={n.targets[0].id:n.value for n in t.body if isinstance(n,ast.Assign)and isinstance(n.targets[0],ast.Name)}
        self.assertEqual(self.fixture(),ast.literal_eval(assign['BINDING']))
        self.assertEqual({k:self.fixture()[k]for k in ['boot','invocation','job','start']},ast.literal_eval(assign['CURRENT']))
        self.assertIn('pg1458-current-day-done-v1',ast.unparse(t))
        self.assertIn('GC_CURRENT_NOT_COMPLETION_PROOF',ast.unparse(t))
    def test_null_missing_wrong_boot(self):
        for bad in [None,{},dict(self.fixture(),boot='old'),dict(self.fixture(),start=True),dict(self.fixture(),run=None)]:
            with self.assertRaises(ValueError):compose(bad)


if __name__=='__main__':unittest.main()
