"""The recorded JVM cwd is data; never silently substitute this operator's cwd."""
from pathlib import Path
import tempfile
import unittest
from pg3688_import_candidate_stage import qualified_classpath


class Classpath(unittest.TestCase):
    def test_literal_trailing_empty_resolves_only_to_recorded_original_cwd(self):
        with tempfile.TemporaryDirectory(prefix='pgpt-classpath-contract-')as d:
            root=Path(d);cwd=root/'qualified-module';cwd.mkdir();jar=root/'library.jar';jar.write_bytes(b'fixed synthetic dependency')
            self.assertEqual(str(jar)+':'+str(cwd),qualified_classpath(str(jar)+':',str(cwd),cwd))
            self.assertEqual(str(jar),qualified_classpath(str(jar),str(cwd),cwd))
            for cp,recorded in [(str(jar)+':','/foreign'),(':'+str(jar),str(cwd)),(str(jar)+'::',str(cwd)),('relative.jar',str(cwd)),(str(root/'missing.jar'),str(cwd)),('',str(cwd))]:
                with self.assertRaises(ValueError):qualified_classpath(cp,recorded,cwd)


if __name__=='__main__':unittest.main()
