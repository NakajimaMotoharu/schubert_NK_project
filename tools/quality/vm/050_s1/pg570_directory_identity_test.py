"""Actual independent TempDir rename/symlink/closedFD negative vectors, no VM mutation."""
import os
from pathlib import Path
import tempfile
import unittest
from pg570_directory_identity import identity, held_directory, fully_absent


class Test(unittest.TestCase):
    def test_normal_dir_content_change_preserves_owned_inode_without_mutating_guard(self):
        with tempfile.TemporaryDirectory(prefix='pg570-dir-') as temporary:
            path = Path(temporary) / 'owned'; path.mkdir(mode=0o700)
            fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
            try:
                expected = identity(os.fstat(fd)); held_directory(fd, path, expected)
                with (path / 'literal').open('xb') as f: f.write(b'independent')
                held_directory(fd, path, expected)
                self.assertEqual((path / 'literal').read_bytes(), b'independent')
                for value in (None, True, -1):
                    with self.assertRaises(ValueError): held_directory(value, path, expected)
                for value in (None, list(expected), (*expected[:4], True, expected[5]),
                              (*expected[:1], expected[1] + 1, *expected[2:])):
                    with self.assertRaises(ValueError): held_directory(fd, path, value)
            finally: os.close(fd)
            with self.assertRaises(OSError): held_directory(fd, path, expected)

    def test_rename_and_same_name_different_inode_cannot_redirect_borrowed_fd(self):
        with tempfile.TemporaryDirectory(prefix='pg570-dir-') as temporary:
            root = Path(temporary); path = root / 'owned'; path.mkdir(mode=0o700)
            fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
            try:
                expected = identity(os.fstat(fd)); path.rename(root / 'retained')
                path.mkdir(mode=0o700)
                with self.assertRaises(ValueError): held_directory(fd, path, expected)
                path.rmdir(); path.symlink_to(root / 'retained', target_is_directory=True)
                with self.assertRaises(ValueError): held_directory(fd, path, expected)
                self.assertEqual(list((root / 'retained').iterdir()), [])
            finally: os.close(fd)

    def test_dangling_symlink_is_not_a_completely_absent_credential_path(self):
        with tempfile.TemporaryDirectory(prefix='pg570-dir-') as temporary:
            path = Path(temporary) / 'credential'
            self.assertTrue(fully_absent(path))
            path.symlink_to(Path(temporary) / 'missing')
            self.assertFalse(path.exists())
            self.assertFalse(fully_absent(path))


if __name__ == '__main__':
    unittest.main()
