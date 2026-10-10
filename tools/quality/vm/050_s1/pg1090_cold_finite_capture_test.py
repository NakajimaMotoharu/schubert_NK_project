"""Independent bytes/inode/xattr/link fixtures; private host directories only."""
import hashlib
import os
from pathlib import Path
import tempfile
import unittest
from pg1090_cold_finite_capture import fd_record,path_record,direct_tree


class Capture(unittest.TestCase):
    def test_held_regular_after_atomic_replacement_has_original_bytes_inode_and_nlink0(self):
        with tempfile.TemporaryDirectory(prefix='pg1090-held-fixture-')as tmp:
            root=Path(tmp);old=root/'current';new=root/'part';old.write_bytes(b'old-original\n');new.write_bytes(b'new-approved\n')
            fd=os.open(old,os.O_RDONLY|os.O_NOFOLLOW)
            try:
                first=fd_record(fd);inode=first['metadata'][1]
                self.assertEqual(hashlib.sha256(b'old-original\n').hexdigest(),first['sha256'])
                os.replace(new,old)
                kept=fd_record(fd);linked=path_record(old)
                self.assertEqual(inode,kept['metadata'][1]);self.assertEqual(0,kept['metadata'][5])
                self.assertEqual(hashlib.sha256(b'old-original\n').hexdigest(),kept['sha256'])
                self.assertNotEqual(inode,linked['metadata'][1]);self.assertEqual(hashlib.sha256(b'new-approved\n').hexdigest(),linked['sha256'])
                self.assertEqual([],kept['acl'])
            finally:os.close(fd)

    def test_complete_direct_tree_includes_every_entry_and_symlink_target(self):
        with tempfile.TemporaryDirectory(prefix='pg1090-tree-fixture-')as tmp:
            root=Path(tmp);(root/'file').write_bytes(b'literal\n');(root/'link').symlink_to('/fixture/absolute');(root/'directory').mkdir()
            value=direct_tree(root)
            self.assertEqual({str(root),str(root/'file'),str(root/'link'),str(root/'directory')},set(value))
            self.assertEqual('/fixture/absolute',value[str(root/'link')]['target'])
            self.assertEqual(hashlib.sha256(b'literal\n').hexdigest(),value[str(root/'file')]['sha256'])
            self.assertEqual([],value[str(root/'link')]['acl'])
            fd=os.open(root,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
            try:self.assertEqual(value[str(root)],fd_record(fd))
            finally:os.close(fd)

    def test_null_invalid_non_directory_and_closed_descriptor_refuse(self):
        for value in (None,-1,False,'0'):
            with self.assertRaises(ValueError):fd_record(value)
        for function in (path_record,direct_tree):
            for value in (None,1,[],{}):
                with self.assertRaises(ValueError):function(value)
        with tempfile.TemporaryDirectory(prefix='pg1090-negative-fixture-')as tmp:
            p=Path(tmp)/'ordinary';p.touch()
            with self.assertRaises(ValueError):direct_tree(p)
            fd=os.open(p,os.O_RDONLY);os.close(fd)
            with self.assertRaises(OSError):fd_record(fd)
            with self.assertRaises(FileNotFoundError):path_record(Path(tmp)/'missing')


if __name__=='__main__':unittest.main()
