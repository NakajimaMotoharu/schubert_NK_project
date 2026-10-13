"""Independent real isolated directory link count, actual generated namespace static0."""
import os
from pathlib import Path
import tempfile
import unittest
from pg1975_current_resume_directory_contract import payload
from pyflakes.api import check


class Current(unittest.TestCase):
    def test_parent_child_independent_native_links(self):
        with tempfile.TemporaryDirectory()as directory:
            parent=Path(directory);child=parent/'unit.d';child.mkdir()
            self.assertEqual(3,os.stat(parent).st_nlink);self.assertEqual(2,os.stat(child).st_nlink)
        raw=payload();self.assertEqual(0,check(raw,'<actual inventory>'))
        self.assertIn('3 if p==runtime else 2',raw)
        self.assertIn('metadata(p)==value[\'metadata\']',raw)
        self.assertIn('native==wanted',raw)


if __name__=='__main__':unittest.main()
