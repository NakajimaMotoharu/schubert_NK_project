import errno
import os
from pathlib import Path
import tempfile
import time
import unittest
from pg1305_ordinary_exchange_io import exchange,move_old_link,linked_attributes


class OrdinaryPhysicalExchangeTest(unittest.TestCase):
    def test_real_atomic_exchange_and_same_old_link_private_move(self):
        with tempfile.TemporaryDirectory(prefix='pg1305-independent-')as value:
            root=Path(value);private=root/'private';private.mkdir(mode=0o700)
            os.symlink('/opt/schubert-nk/releases/0.1.0-PG1068',root/'current')
            os.symlink('/opt/schubert-nk/releases/0.1.0-PG1292',root/'pg1305-current.part')
            directory=os.open(root,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
            target=os.open(private,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
            held=os.open(root/'current',os.O_PATH|os.O_NOFOLLOW)
            try:
                old=linked_attributes(directory,'current',held);begin=time.time_ns()
                exchange(directory,'pg1305-current.part')
                self.assertEqual(os.readlink(root/'current'),'/opt/schubert-nk/releases/0.1.0-PG1292')
                exchanged=linked_attributes(directory,'pg1305-current.part',held)
                self.assertEqual(old['metadata'][:8],exchanged['metadata'][:8])
                self.assertEqual(exchanged['target'],'/opt/schubert-nk/releases/0.1.0-PG1068')
                saved=move_old_link(directory,target,held);end=time.time_ns()
                self.assertFalse(os.path.lexists(root/'pg1305-current.part'))
                self.assertEqual(os.readlink(private/'current-link.private'),'/opt/schubert-nk/releases/0.1.0-PG1068')
                self.assertEqual(old['metadata'][:8],saved['metadata'][:8])
                self.assertEqual(saved['metadata'][5],1)
                self.assertEqual(saved['acl'],old['acl'])
                self.assertLessEqual(begin,saved['metadata'][8]);self.assertLessEqual(saved['metadata'][8],end)
            finally:os.close(held);os.close(target);os.close(directory)

    def test_exact_arguments_fault_no_retry_and_namespace_unchanged(self):
        with tempfile.TemporaryDirectory(prefix='pg1305-negative-')as value:
            root=Path(value);os.symlink('old',root/'current');os.symlink('new',root/'pg1305-current.part')
            fd=os.open(root,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
            try:
                calls=[]
                def fail(directory,stage):calls.append((directory,stage));return -1,errno.EIO
                with self.assertRaises(OSError)as caught:exchange(fd,'pg1305-current.part',fail)
                self.assertEqual(caught.exception.errno,errno.EIO);self.assertEqual(calls,[(fd,'pg1305-current.part')])
                self.assertEqual(os.readlink(root/'current'),'old');self.assertEqual(os.readlink(root/'pg1305-current.part'),'new')
                for directory,stage,call in [(None,'pg1305-current.part',fail),(True,'pg1305-current.part',fail),(-1,'pg1305-current.part',fail),(fd,None,fail),(fd,'../current',fail),(fd,'pg1088-current.part',fail),(fd,'pg1305-current.part',None)]:
                    with self.assertRaises(ValueError):exchange(directory,stage,call)
                self.assertEqual(len(calls),1)
            finally:os.close(fd)

    def test_private_destination_exists_or_atomic_race_refuses_without_overwrite(self):
        with tempfile.TemporaryDirectory(prefix='pg1305-race-')as value:
            root=Path(value);private=root/'private';private.mkdir(mode=0o700)
            os.symlink('/opt/schubert-nk/releases/0.1.0-PG1068',root/'pg1305-current.part')
            directory=os.open(root,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
            target=os.open(private,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
            held=os.open(root/'pg1305-current.part',os.O_PATH|os.O_NOFOLLOW)
            try:
                calls=[]
                def race(src,dst):
                    calls.append((src,dst));return -1,errno.EEXIST
                with self.assertRaises(OSError)as error:move_old_link(directory,target,held,race)
                self.assertEqual(error.exception.errno,errno.EEXIST);self.assertEqual(len(calls),1)
                self.assertTrue(os.path.lexists(root/'pg1305-current.part'));self.assertFalse(os.path.lexists(private/'current-link.private'))
                os.symlink('/independent/foreign',private/'current-link.private')
                with self.assertRaises(FileExistsError):move_old_link(directory,target,held,race)
                self.assertEqual(len(calls),1)
                self.assertEqual(os.readlink(private/'current-link.private'),'/independent/foreign')
                self.assertEqual(os.readlink(root/'pg1305-current.part'),'/opt/schubert-nk/releases/0.1.0-PG1068')
            finally:os.close(held);os.close(target);os.close(directory)


if __name__=='__main__':unittest.main()
