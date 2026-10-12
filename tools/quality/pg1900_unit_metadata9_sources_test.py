"""Actual verify handles relatime, rejecting every SS9 field/inode/chrono mutation."""
import copy
import stat
import types
import unittest
from unittest.mock import patch
from pg1900_unit_metadata9_sources import source


def record(ino,size,mtime,ctime,atime):
    return types.SimpleNamespace(st_dev=1,st_ino=ino,st_uid=0,st_gid=0,st_mode=stat.S_IFREG|0o644,st_nlink=1,st_size=size,st_mtime_ns=mtime,st_ctime_ns=ctime,st_atime_ns=atime)


class Metadata(unittest.TestCase):
    def setUp(self):
        self.module=types.ModuleType('actual_fixed_unit')
        exec(compile(source(),'<whole actual metadata9 Unit>','exec'),self.module.__dict__)

    def exercise(self,named=None,new=None):
        obj=self.module.UnitExchange.__new__(self.module.UnitExchange)
        obj.exchanged=True;obj.old=1;obj.private=2;obj.directory=3
        obj.old_attributes=record(41,1836,10,11,12);obj.begin_ns=20;obj.names=['one','two']
        old=record(41,1836,10,30,12)
        named=named or record(41,1836,10,30,99)
        new=new or record(42,1947,31,32,33)
        with patch.object(self.module,'attributes',side_effect=[old,new]),patch.object(self.module.os,'stat',return_value=named),patch.object(self.module.os,'open',return_value=4),patch.object(self.module.os,'close'),patch.object(self.module.os.path,'lexists',return_value=False),patch.object(self.module.os,'listdir',return_value=['one','two']),patch.object(self.module.time,'time_ns',return_value=50):
            obj.verify()

    def test_actual_read_atime_difference_accepted_with_exact_nine_fields(self):
        self.exercise()
        self.assertEqual((1,41,0,0,stat.S_IFREG|0o644,1,1836,10,30),self.module.metadata9(record(41,1836,10,30,99)))

    def test_all_nine_fields_remain_required_and_future_or_same_new_inode_refused(self):
        base=record(41,1836,10,30,99)
        for name in ['st_dev','st_ino','st_uid','st_gid','st_mode','st_nlink','st_size','st_mtime_ns','st_ctime_ns']:
            bad=copy.copy(base);setattr(bad,name,getattr(bad,name)+1)
            with self.assertRaises(ValueError):self.exercise(named=bad)
        for new in [record(41,1947,31,32,33),record(42,1947,19,32,33),record(42,1947,31,51,33)]:
            with self.assertRaises(ValueError):self.exercise(new=new)


if __name__=='__main__':unittest.main()
