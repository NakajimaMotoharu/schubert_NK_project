"""Exact cold source/clock counterexample, no subtraction/tolerance or fallback."""
import ast
import types
import unittest
from unittest.mock import Mock
import pg2950_current_cold_resume_sources as p


class CurrentCold(unittest.TestCase):
    def test_complete_source_current_and_proven_cold_boundary(self):
        values=p.sources();self.assertEqual(20,len(values))
        refs=values['pg2950_native_refs.py']
        self.assertIn('mutation_begin_ns=metadata_lower_ns()',refs)
        self.assertNotIn('mutation_begin_ns=time.time_ns()',refs)
        self.assertIn('runtime_before[str(runtime_root)]',refs)
        self.assertNotIn('runtime_before[str(runtime_directory)]',refs)
        self.assertIn('os.mkdir(UNIT,0o700,dir_fd=root)',values['pg2950_runtime_writer.py'])
        for v in [p.SOURCE,p.BOM,p.RUN,p.BOOT]:self.assertTrue(v in values[p.CLASS+'.java'],v)

    def test_actual_coarse_lower_not_fine_or_invented_margin(self):
        raw=p.sources()['pg2950_native_refs.py'];tree=ast.parse(raw)
        node=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='metadata_lower_ns')
        clock=Mock();clock.clock_getres.return_value=.01;clock.time_ns.side_effect=[1004,1006];clock.clock_gettime_ns.return_value=1000
        def require(v):
            if not v:raise ValueError('clock denied')
        ns={'time':clock,'require':require};exec(ast.get_source_segment(raw,node),ns)
        self.assertEqual(1000,ns['metadata_lower_ns']());clock.clock_gettime_ns.assert_called_once_with(5)
        clock.time_ns.side_effect=[1004,1006];clock.clock_gettime_ns.side_effect=OSError('independent coarse clock unavailable')
        with self.assertRaises(OSError):ns['metadata_lower_ns']()
        module=types.ModuleType('contract');exec(p.sources()['pg2950_resume_contract.py'],module.__dict__)
        import hashlib,stat
        data=b'[Service]\nExecStart=fixed\n';row=lambda x,h=None:{'metadata':x,'sha256':h}
        before={module.RUNTIME:row([1,10,0,0,stat.S_IFDIR|0o755,2,40,900,900])}
        actual={module.RUNTIME:row([1,10,0,0,stat.S_IFDIR|0o755,3,60,1001,1001]),module.DIRECTORY:row([1,11,0,0,stat.S_IFDIR|0o755,2,60,1001,1001]),module.TARGET:row([1,12,0,0,stat.S_IFREG|0o644,1,len(data),1001,1001],hashlib.sha256(data).hexdigest())}
        self.assertTrue(module.runtime_tree(before,actual,data,1000,1006))
        self.assertFalse(module.runtime_tree(before,actual,data,1004,1006))


if __name__=='__main__':unittest.main()
