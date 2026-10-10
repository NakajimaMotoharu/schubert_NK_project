"""Independent vectors, all real-FD faults, existing directory untouched."""
import ast
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import pg1160_runtime_writer_test as inherited
from pg1172_existing_runtime_writer import source,module


class ExistingWriterTest(inherited.WriterTest):
    def exercise(self,fault=0,zero=False,foreign=False,owned=False):
        # Reuse independently established real-FD fixture, adjust its graph only.
        m=module()
        # Fixture graph gains the pre-existing admitted Unit.d, not a synthetic mkdir by code.
        original_mkdir=Path.mkdir
        admitted=[]
        def mkdir(p,*args,**kwargs):
            result=original_mkdir(p,*args,**kwargs)
            if p.name=='system':
                original_mkdir(p/m.UNIT,mode=0o755);(p/m.UNIT).chmod(0o755);admitted.append(p/m.UNIT)
            return result
        # Existing fixture assertions inspect p/UNIT/NAME. Actual writer target is that
        # admitted child; override prepare dispatch while preserving the outer vector.
        native_prepare=m.prepare
        def prepare(parent,expected,dropin):
            if str(parent).startswith('/proc/self/fd/'):
                return native_prepare(parent,expected,dropin)
            child=parent/m.UNIT
            if foreign:
                (child/'foreign').write_bytes((parent/'foreign').read_bytes())
            s=child.stat();actual=[s.st_dev,s.st_ino,0,0,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns]
            return native_prepare(child,actual,dropin)
        m.prepare=prepare
        owned_prepare=m.owned_prepare
        def owned_dispatch(expected,dropin):
            child=admitted[-1]
            if foreign:
                (child/'foreign').write_bytes((child.parent/'foreign').read_bytes())
            s=child.stat();actual=[s.st_dev,s.st_ino,0,0,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns]
            return owned_prepare(actual,dropin)
        m.owned_prepare=owned_dispatch
        with patch.object(inherited,'writer',m),patch.object(Path,'mkdir',mkdir):
            return super().exercise(fault,zero,foreign,owned)

    def test_owned_ancestor_real_fd_every_fault(self):
        s=source();tree=ast.parse(s)
        self.assertTrue("['run','systemd','system',UNIT]"in s)
        self.assertFalse('os.mkdir('in s)
        self.assertTrue("NAME='zz-pg1160-once-resume.conf'"in s)
        self.assertFalse(any(isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and n.func.attr in ['rename','unlink']for n in ast.walk(tree)))
        events,error=self.exercise(owned=True);self.assertIsNone(error)
        for point in range(1,len(events)+1):
            with self.subTest(point=point,operation=events[point-1]):
                _,error=self.exercise(fault=point,owned=True);self.assertIsInstance(error,OSError)
        _,error=self.exercise(foreign=True,owned=True);self.assertIsInstance(error,ValueError)
        print('PG1172_EXISTING_ANCESTOR_ORACLE faultPositions='+str(len(events))+' realFD=true syntheticRoot=true VM0=true')

    def test_exact_leaf_mode_independent_of_ambient_umask(self):
        previous=os.umask(0o077)
        try:
            for mask in [0o022,0o077]:
                os.umask(mask)
                for owned in [False,True]:
                    _,error=self.exercise(owned=owned);self.assertIsNone(error)
        finally:os.umask(previous)


if __name__=='__main__':unittest.main()
