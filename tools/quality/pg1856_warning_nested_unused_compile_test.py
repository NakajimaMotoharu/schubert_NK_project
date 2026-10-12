"""Actual nested writer, strict path negatives, recursive pinned inventory."""
import pathlib
import tempfile
import unittest
from unittest.mock import patch
import pg1856_warning_nested_unused_compile as module


class Nested(unittest.TestCase):
    def test_actual_new_nested_relative_write_and_canonical_escape_rejection(self):
        with tempfile.TemporaryDirectory(prefix='pg1856-writer-')as directory:
            root=pathlib.Path(directory)
            with patch.object(module,'TARGET',root):
                path=root/'dev/codex/fixture.class';module.write(path,b'independent-bytes')
                self.assertEqual(b'independent-bytes',path.read_bytes())
                self.assertEqual(0o700,path.parent.stat().st_mode&0o777)
                self.assertEqual({'dev/codex/fixture.class'},set(module.inventory(root)))
                with self.assertRaises(ValueError):module.write(root/'bad/../escape.class',b'x')
        raw=module.compiler();self.assertIn('hashes = inventory(TARGET)',raw)
        self.assertIn('pg1856-frozen-v1.safe.json',raw)
        self.assertNotIn('p.name: sha(p)',raw)


if __name__=='__main__':unittest.main()
