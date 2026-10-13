import ast
import unittest
from pg2330_current_existing_runtime_finish_sources import sources,CLASS,BEFORE


class ExistingFinish(unittest.TestCase):
    def test_same_inode_only_reload_and_current_loaded_baseline(self):
        values=sources();self.assertEqual(20,len(values))
        refs=values['pg2330_native_refs.py']
        for value in [BEFORE,"json.loads(original)['before']['rows']","json.loads(baseline)['before']",'same_value(now,first)','pinned_runtime.reload();placed=True']:
            self.assertTrue(value in refs,'missing exact existing boundary '+value)
        self.assertNotIn('runtime.owned_prepare',refs)
        self.assertNotIn('mutation_begin_ns',refs)
        io=values['pg2330_existing_runtime.py']
        for value in ['28,4224','28,4223','zz-pg2316-once-resume.conf','888ee8561e9c25da302470c2561cdbf65cbf10cdebf668f7196f27b485bc5035']:
            self.assertIn(value,io)
        self.assertFalse(any(isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and n.func.attr in {'mkdir','unlink','rename','replace','chmod','fchmod'}for n in ast.walk(ast.parse(io))))
        self.assertIn('ONLY_EXISTING_RUNTIME_RELOAD',values[CLASS+'.java'])
        self.assertIn('State.ISSUED',values[CLASS+'.java'])


if __name__=='__main__':unittest.main()
