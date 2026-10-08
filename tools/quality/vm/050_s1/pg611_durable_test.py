import os
import pathlib
import stat
import tempfile
import unittest
from unittest.mock import patch
from pg611_durable import save


class Test(unittest.TestCase):
    def test_file_directory_order_and_each_failure_before_ack(self):
        for failure in (0,1,2):
            with tempfile.TemporaryDirectory(prefix='pg611-owned-fixture-')as name:
                root=pathlib.Path(name);events=[]
                def sync(fd):
                    events.append('directory'if stat.S_ISDIR(os.fstat(fd).st_mode)else 'file')
                    if len(events)==failure:raise OSError('independent fixture')
                with patch('pg611_durable.os.fsync',side_effect=sync):
                    if failure:
                        with self.assertRaises(OSError):save(root,'one',b'oneOwnedStop=true\n')
                    else:save(root,'one',b'oneOwnedStop=true\n');events.append('ACK')
                self.assertEqual(events,(['file','directory','ACK']if not failure else ['file','directory'][:failure]))
                self.assertEqual((root/'one').read_bytes(),b'oneOwnedStop=true\n')
                with self.assertRaises(FileExistsError):save(root,'one',b'changed')
    def test_name_inputs_and_path_replacement(self):
        for root,name,data in ((None,'one',b'x'),(pathlib.Path('/not-used'),None,b'x'),(pathlib.Path('/not-used'),'../other',b'x'),(pathlib.Path('/not-used'),'one',None)):
            with self.assertRaises(ValueError):save(root,name,data)
        with tempfile.TemporaryDirectory(prefix='pg611-owned-fixture-')as name:
            base=pathlib.Path(name);root=base/'owned';root.mkdir(mode=0o700);calls=[]
            def swap(fd):
                calls.append(fd)
                if len(calls)==2:root.rename(base/'preserved');root.mkdir(mode=0o700)
            with patch('pg611_durable.os.fsync',side_effect=swap):
                with self.assertRaises(ValueError):save(root,'one',b'private fixture')
            self.assertEqual((base/'preserved'/'one').read_bytes(),b'private fixture');self.assertEqual(list(root.iterdir()),[])


if __name__=='__main__':unittest.main()
