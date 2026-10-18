import unittest
import os
import tempfile
from pathlib import Path
from pyflakes.api import check,checkPath
import pg5436_current_full11_view as entry


class StrictProjection(unittest.TestCase):
    def test_actual_original_snapshot_bound_and_no_implicit_requalification(self):
        raw=entry.payload()
        self.assertIn("'4ab25ad070358ef6580a29855c2cbd1fe00f9cb32f6a514bc279a932bcd0ba94'",raw)
        self.assertIn("'snapshotReadTimeIsOriginal5434':True",raw)
        self.assertIn("sum(p.endswith('.exec')for p in view['native'])==88",raw)
        self.assertNotIn('subprocess',raw)
        self.assertEqual(len(set(entry.FIELDS)),11)
        self.assertEqual(check(raw,'<strict full11 projection>'),0)
        for path in(entry.__file__,__file__):self.assertEqual(checkPath(path),0)

    def test_stale_atime_kept_without_weakening_full_stat_equality(self):
        with tempfile.TemporaryDirectory()as folder:
            path=Path(folder)/'fixed';path.write_bytes(b'independent fixed fixture')
            os.utime(path,ns=(1_000_000_000,2_000_000_000));before=path.lstat()
            fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC|os.O_NOATIME)
            try:
                self.assertEqual(os.pread(fd,before.st_size+1,0),b'independent fixed fixture')
                self.assertEqual(os.fstat(fd),before)
                self.assertEqual(path.lstat(),before)
            finally:os.close(fd)
        self.assertIn('os.O_CLOEXEC|os.O_NOATIME',entry.payload())


if __name__=='__main__':unittest.main()
