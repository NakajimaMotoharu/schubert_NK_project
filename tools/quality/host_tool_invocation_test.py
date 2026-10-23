"""Owned temporary fixtures only; BUG1648/YKT1401 no target/runtime operations."""
import hashlib
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import host_tool_invocation as tool


class InvocationContractTest(unittest.TestCase):
    def setUp(self):
        self.temporary=tempfile.TemporaryDirectory(prefix='pgpt-invocation-')
        self.addCleanup(self.temporary.cleanup)
        self.root=Path(self.temporary.name)
        self.folder=self.root/'tools/quality';self.folder.mkdir(parents=True)
        self.entry=self.folder/'entry.py';self.entry.write_text('# entry\n')
        self.library=self.folder/'library.py';self.library.write_text('# library\n')

    def observe(self,argv,original):
        with patch.object(sys,'argv',argv),patch.object(sys,'orig_argv',original):
            return tool.capture(self.library,self.root)

    def test_actual_entry_and_library_are_distinct_and_hashed(self):
        argv=[str(self.entry)]
        for flags in ([],['-B']):
            original=['python3',*flags,*argv]
            value=self.observe(argv,original)
            self.assertEqual(value['actualPythonCommand'],original)
            self.assertEqual(value['entrypointPath'],'tools/quality/entry.py')
            self.assertEqual(value['libraryPath'],'tools/quality/library.py')
            self.assertEqual(value['entrypointSha256'],hashlib.sha256(b'# entry\n').hexdigest())
            self.assertEqual(value['librarySha256'],hashlib.sha256(b'# library\n').hexdigest())
            self.assertFalse(value['arbitraryArgumentsRecorded'])
            tool.verify(value,self.root)

    def test_tool_mutation_cannot_be_qualified(self):
        value=self.observe([str(self.entry)],['python3','-B',str(self.entry)])
        self.library.write_text('# deliberately changed own fixture\n')
        with self.assertRaisesRegex(ValueError,'public tool source changed'):
            tool.verify(value,self.root)

    def test_arguments_and_ambiguous_interpreter_not_serialized(self):
        for argv,original in (
          ([],[]),([''],['python3','']),([str(self.entry),'opaque'],['python3',str(self.entry),'opaque']),
          ([str(self.entry)],['other',str(self.entry)]),([str(self.entry)],['python3','-c',str(self.entry)]),
          ([str(self.entry)],['python3','different.py']),([str(self.entry)],['python3',1])):
            with self.assertRaises(ValueError):self.observe(argv,original)

    def test_missing_outside_symlink_and_non_python_refused(self):
        outside=self.root/'outside.py';outside.write_text('# own fixture\n')
        link=self.folder/'link.py';link.symlink_to(self.entry)
        text=self.folder/'entry.txt';text.write_text('# own fixture\n')
        for path in (outside,link,text,self.folder/'missing.py',self.folder):
            with self.assertRaises(ValueError):self.observe([str(path)],['python3',str(path)])
        with patch.object(sys,'argv',[str(self.entry)]),patch.object(sys,'orig_argv',['python3',str(self.entry)]):
            with self.assertRaises(ValueError):tool.capture(outside,self.root)


if __name__=='__main__':
    unittest.main()
