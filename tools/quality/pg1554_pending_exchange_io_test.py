import errno
import os
from pathlib import Path
import tempfile
import time
import unittest
from pg1554_pending_exchange_io import exchange,move_old_link,linked_attributes

class PendingExchangeTest(unittest.TestCase):
    def test_real_current_exchange_and_linked_original_private(self):
        with tempfile.TemporaryDirectory(prefix='pg1554-real-fd-')as d:
            root=Path(d);private=root/'private';private.mkdir()
            os.symlink('/opt/schubert-nk/releases/0.1.0-PG1292',root/'current')
            os.symlink('/opt/schubert-nk/releases/0.1.0-PG1544',root/'pg1551-current.part')
            parent=os.open(root,os.O_RDONLY|os.O_DIRECTORY);save=os.open(private,os.O_RDONLY|os.O_DIRECTORY);held=os.open(root/'current',os.O_PATH|os.O_NOFOLLOW)
            try:
                old=linked_attributes(parent,'current',held);begin=time.time_ns();exchange(parent,'pg1551-current.part')
                self.assertEqual(os.readlink(root/'current'),'/opt/schubert-nk/releases/0.1.0-PG1544')
                saved=move_old_link(parent,save,held);end=time.time_ns()
                self.assertEqual(saved['metadata'][:8],old['metadata'][:8]);self.assertEqual(saved['metadata'][5],1)
                self.assertEqual(os.readlink(private/'current-link.private'),'/opt/schubert-nk/releases/0.1.0-PG1292')
                self.assertFalse(os.path.lexists(root/'pg1551-current.part'));self.assertLessEqual(begin,saved['metadata'][8]);self.assertLessEqual(saved['metadata'][8],end)
            finally:os.close(held);os.close(save);os.close(parent)

    def test_io_fault_exact_arguments_and_no_retry(self):
        with tempfile.TemporaryDirectory(prefix='pg1554-fault-')as d:
            root=Path(d);os.symlink('OLD',root/'current');os.symlink('NEW',root/'pg1551-current.part');fd=os.open(root,os.O_RDONLY|os.O_DIRECTORY)
            try:
                calls=[]
                def fail(a,b):calls.append((a,b));return -1,errno.EIO
                with self.assertRaises(OSError)as err:exchange(fd,'pg1551-current.part',fail)
                self.assertEqual(err.exception.errno,errno.EIO);self.assertEqual(len(calls),1)
                for a,b,c in [(None,'pg1551-current.part',fail),(True,'pg1551-current.part',fail),(fd,None,fail),(fd,'../current',fail),(fd,'pg1305-current.part',fail),(fd,'pg1551-current.part',None)]:
                    with self.assertRaises(ValueError):exchange(a,b,c)
                self.assertEqual(len(calls),1);self.assertEqual(os.readlink(root/'current'),'OLD');self.assertEqual(os.readlink(root/'pg1551-current.part'),'NEW')
            finally:os.close(fd)

    def test_destination_race_preserves_old_inode_and_foreign_link(self):
        with tempfile.TemporaryDirectory(prefix='pg1554-race-')as d:
            root=Path(d);private=root/'private';private.mkdir();os.symlink('/opt/schubert-nk/releases/0.1.0-PG1292',root/'pg1551-current.part')
            parent=os.open(root,os.O_RDONLY|os.O_DIRECTORY);save=os.open(private,os.O_RDONLY|os.O_DIRECTORY);held=os.open(root/'pg1551-current.part',os.O_PATH|os.O_NOFOLLOW)
            try:
                calls=[]
                def race(a,b):calls.append((a,b));return -1,errno.EEXIST
                with self.assertRaises(OSError):move_old_link(parent,save,held,race)
                self.assertEqual(len(calls),1);self.assertTrue(os.path.lexists(root/'pg1551-current.part'))
                os.symlink('/foreign',private/'current-link.private')
                with self.assertRaises(FileExistsError):move_old_link(parent,save,held,race)
                self.assertEqual(len(calls),1);self.assertEqual(os.readlink(private/'current-link.private'),'/foreign')
            finally:os.close(held);os.close(save);os.close(parent)

if __name__=='__main__':unittest.main()
