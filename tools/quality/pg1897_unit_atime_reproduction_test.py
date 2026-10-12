"""Independent real filesystem relatime vector; SS metadata9 stays complete."""
import os
from pathlib import Path
import tempfile
import unittest


def nine(s):
    return (s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)


class Relatime(unittest.TestCase):
    def test_real_read_changes_only_atime_and_breaks_full_stat_equality(self):
        with tempfile.TemporaryDirectory()as root:
            p=Path(root)/'old';p.write_bytes(b'independent old Unit bytes')
            os.utime(p,ns=(1,2))
            fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW)
            try:
                before=os.fstat(fd);raw=os.pread(fd,before.st_size+1,0);after=p.stat()
                self.assertEqual(b'independent old Unit bytes',raw)
                self.assertGreater(after.st_atime_ns,before.st_atime_ns)
                self.assertNotEqual(before,after)
                self.assertEqual(nine(before),nine(after))
            finally:os.close(fd)


if __name__=='__main__':unittest.main()
