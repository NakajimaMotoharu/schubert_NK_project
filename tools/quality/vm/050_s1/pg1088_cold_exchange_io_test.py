"""Private temporary directory only, independent old/new link and errno vectors."""
import errno
import os
from pathlib import Path
import tempfile
import unittest
from pg1088_cold_exchange_io import exchange,linked_attributes


class Exchange(unittest.TestCase):
    def test_stale_atime_readlink_observation_keeps_complete_contract_identity(self):
        with tempfile.TemporaryDirectory(prefix='pg1088-stale-atime-fixture-')as tmp:
            root=Path(tmp);(root/'current').symlink_to('/fixture/old');(root/'pg1088-current.part').symlink_to('/fixture/new')
            os.utime(root/'current',ns=(1,1),follow_symlinks=False)
            fd=os.open(root,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
            old=os.open('current',os.O_PATH|os.O_NOFOLLOW,dir_fd=fd)
            try:
                exchange(fd,'pg1088-current.part');first=os.fstat(old)
                expected=[first.st_dev,first.st_ino,first.st_uid,first.st_gid,first.st_mode,
                          first.st_nlink,first.st_size,first.st_mtime_ns,first.st_ctime_ns]
                row=linked_attributes(fd,'pg1088-current.part',old)
                self.assertEqual(expected,row['metadata']);self.assertEqual('/fixture/old',row['target'])
                self.assertEqual([],row['acl']);self.assertNotEqual(first.st_atime_ns,os.fstat(old).st_atime_ns)
            finally:os.close(old);os.close(fd)

    def test_actual_exchange_preserves_public_presence_old_inode_link_target_and_attrs(self):
        with tempfile.TemporaryDirectory(prefix='pg1088-exchange-fixture-')as tmp:
            root=Path(tmp);(root/'current').symlink_to('/fixture/old');(root/'pg1088-current.part').symlink_to('/fixture/new')
            fd=os.open(root,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
            old=os.open('current',os.O_PATH|os.O_NOFOLLOW,dir_fd=fd)
            new=os.open('pg1088-current.part',os.O_PATH|os.O_NOFOLLOW,dir_fd=fd)
            try:
                old_inode=os.fstat(old).st_ino;new_inode=os.fstat(new).st_ino
                self.assertNotEqual(old_inode,new_inode)
                self.assertEqual('/fixture/old',linked_attributes(fd,'current',old)['target'])
                exchange(fd,'pg1088-current.part')
                self.assertEqual('/fixture/new',os.readlink('current',dir_fd=fd))
                self.assertEqual(new_inode,os.stat('current',dir_fd=fd,follow_symlinks=False).st_ino)
                row=linked_attributes(fd,'pg1088-current.part',old)
                self.assertEqual('/fixture/old',row['target']);self.assertEqual(old_inode,row['metadata'][1]);self.assertEqual(1,row['metadata'][5]);self.assertEqual([],row['acl'])
                os.mkdir('private',mode=0o700,dir_fd=fd);private=os.open('private',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=fd)
                try:
                    os.rename('pg1088-current.part','current-link.private',src_dir_fd=fd,dst_dir_fd=private)
                    os.fsync(fd);os.fsync(private)
                    self.assertEqual('/fixture/old',linked_attributes(private,'current-link.private',old)['target'])
                    self.assertEqual('/fixture/new',os.readlink('current',dir_fd=fd))
                    self.assertEqual(1,os.fstat(old).st_nlink)
                finally:os.close(private)
            finally:os.close(new);os.close(old);os.close(fd)

    def test_invalid_null_unknown_fd_stage_and_callback_do_not_call(self):
        calls=[]
        def callback(*args):calls.append(args);return 0,0
        for fd,name,call in [(None,'pg1088-current.part',callback),(-1,'pg1088-current.part',callback),
          (False,'pg1088-current.part',callback),(0,None,callback),(0,'../escape',callback),
          (0,'current',callback),(0,'pg1088-current.part',None)]:
            with self.assertRaises(ValueError):exchange(fd,name,call)
        self.assertEqual([],calls)

    def test_error_unknown_never_retries_or_falls_back(self):
        with tempfile.TemporaryDirectory(prefix='pg1088-errno-fixture-')as tmp:
            root=Path(tmp);(root/'current').symlink_to('/fixture/old');(root/'pg1088-current.part').symlink_to('/fixture/new')
            fd=os.open(root,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
            try:
                for code in (errno.EIO,errno.EXDEV,errno.ENOENT,errno.EPERM,errno.ENOSYS):
                    calls=[]
                    def fault(*args):calls.append(args);return -1,code
                    with self.assertRaises(OSError)as found:exchange(fd,'pg1088-current.part',fault)
                    self.assertEqual(code,found.exception.errno);self.assertEqual(1,len(calls))
                    self.assertEqual('/fixture/old',os.readlink(root/'current'))
                    self.assertEqual('/fixture/new',os.readlink(root/'pg1088-current.part'))
            finally:os.close(fd)

    def test_link_replacement_missing_alias_nonlink_and_unknown_name_refuse(self):
        with tempfile.TemporaryDirectory(prefix='pg1088-link-fixture-')as tmp:
            root=Path(tmp);(root/'current').symlink_to('/fixture/old');(root/'ordinary').touch()
            fd=os.open(root,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
            old=os.open('current',os.O_PATH|os.O_NOFOLLOW,dir_fd=fd);ordinary=os.open('ordinary',os.O_RDONLY,dir_fd=fd)
            try:
                for name in (None,'','../outside','a/b','.','..'):
                    with self.assertRaises(ValueError):linked_attributes(fd,name,old)
                with self.assertRaises(ValueError):linked_attributes(fd,'ordinary',ordinary)
                os.rename('current','saved',src_dir_fd=fd,dst_dir_fd=fd)
                with self.assertRaises(FileNotFoundError):linked_attributes(fd,'current',old)
                os.symlink('/fixture/foreign','current',dir_fd=fd)
                with self.assertRaises(ValueError):linked_attributes(fd,'current',old)
                self.assertEqual('/fixture/old',linked_attributes(fd,'saved',old)['target'])
            finally:os.close(ordinary);os.close(old);os.close(fd)


if __name__=='__main__':unittest.main()
