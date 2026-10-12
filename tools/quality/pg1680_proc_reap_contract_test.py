"""Independent errno and PID-reuse negative matrix."""
import errno
import unittest
from pg1680_proc_reap_contract import confirmed_absence


class ProcReapTest(unittest.TestCase):
    def test_terminal_only_with_current_absence(self):
        for code in [errno.ENOENT,errno.ESRCH]:
            self.assertTrue(confirmed_absence(OSError(code,'race'),False))
            self.assertFalse(confirmed_absence(OSError(code,'race'),True))
        for code in [errno.EPERM,errno.EIO,errno.EACCES,errno.EINVAL,0,None]:
            self.assertFalse(confirmed_absence(OSError(code,'refused'),False))
        for bad in [None,True,ValueError('unknown')]:
            with self.assertRaises(ValueError):confirmed_absence(bad,False)
        for bad in [None,0,1,'false']:
            with self.assertRaises(ValueError):confirmed_absence(OSError(errno.ESRCH,'race'),bad)


if __name__=='__main__':unittest.main()
