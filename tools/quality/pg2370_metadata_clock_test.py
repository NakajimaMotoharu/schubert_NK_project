"""Independent clock vectors and literal tmpfs metadata boundary for BUG1232."""
import ast
import hashlib
import stat
import types
import unittest
from unittest.mock import Mock
from pg2316_current_cold_resume_sources import sources


class MetadataClock(unittest.TestCase):
    def module(self,fine,coarse,resolution=.001):
        s=sources()['pg2316_native_refs.py'];t=ast.parse(s)
        n=next(n for n in t.body if isinstance(n,ast.FunctionDef)and n.name=='metadata_lower_ns')
        clock=types.SimpleNamespace(clock_getres=Mock(return_value=resolution),time_ns=Mock(side_effect=fine),clock_gettime_ns=Mock(return_value=coarse))
        def require(v):
            if not v:raise ValueError('independent clock contract')
        ns={'time':clock,'require':require};exec(ast.get_source_segment(s,n),ns)
        return ns['metadata_lower_ns'],clock

    def test_actual_coarse_lower_no_margin_or_fallback(self):
        call,clock=self.module([105,107],100)
        self.assertEqual(100,call());clock.clock_getres.assert_called_once_with(5);clock.clock_gettime_ns.assert_called_once_with(5)
        for fine,coarse,res in [([105,104],100,.001),([105,107],108,.001),([105,107],0,.001),([105,107],None,.001),([105,107],True,.001),([105,107],100,0.0),([105,107],100,None),([105,107],100,2.0)]:
            with self.assertRaises(ValueError):self.module(fine,coarse,res)[0]()
        call,clock=self.module([105,107],100);clock.clock_gettime_ns.side_effect=OSError('unsupported clock')
        with self.assertRaises(OSError):call()

    def test_literal_inode_boundary_not_precision_tolerance(self):
        v=sources();ns={};exec(v['pg2316_resume_contract.py'],ns)
        r='/run/systemd/system';d=r+'/schubert-nk-morning-controller.service.d';p=d+'/zz-pg2316-once-resume.conf';data=b'literal\n'
        row=lambda m,h=None:{'metadata':m,'sha256':h}
        old={r:row([28,3,0,0,stat.S_IFDIR|0o755,2,40,50,50])}
        new={r:row([28,3,0,0,stat.S_IFDIR|0o755,3,60,100,100]),d:row([28,12,0,0,stat.S_IFDIR|0o755,2,60,106,106]),p:row([28,13,0,0,stat.S_IFREG|0o644,1,len(data),106,106],hashlib.sha256(data).hexdigest())}
        self.assertFalse(ns['runtime_tree'](old,new,data,105,107))
        lower=self.module([105,107],100)[0]();self.assertTrue(ns['runtime_tree'](old,new,data,lower,107))
        self.assertFalse(ns['runtime_tree'](old,new,data,101,107));self.assertFalse(ns['runtime_tree'](old,new,data,100,105))
        self.assertIn('mutation_begin_ns=metadata_lower_ns()',v['pg2316_native_refs.py'])
        self.assertNotIn('mutation_begin_ns=time.time_ns()',v['pg2316_native_refs.py'])


if __name__=='__main__':unittest.main()
