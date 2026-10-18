import inspect
import hashlib
import tempfile
import unittest
from pathlib import Path
from pyflakes.api import check,checkPath
import pg5414_ownership_whole as entry


class OwnershipWhole(unittest.TestCase):
    def test_partial_archive_resume_is_exact_and_never_replays_started_namespace(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);out=root/'partial';out.mkdir();archive=out/'source.tar'
            archive.write_bytes(b'fixture immutable archive')
            digest=hashlib.sha256(archive.read_bytes()).hexdigest()
            self.assertEqual(entry.validate_partial(out,digest),archive)
            with self.assertRaises(ValueError):entry.validate_partial(out,'0'*64)
            marker=out/'begin.safe.json';marker.write_bytes(b'issued')
            with self.assertRaises(ValueError):entry.validate_partial(out,digest)
            marker.unlink();archive.unlink();archive.symlink_to(root/'missing')
            with self.assertRaises(ValueError):entry.validate_partial(out,digest)
            with self.assertRaises(ValueError):entry.validate_partial(root/'absent',digest)
    def test_literal_inventory_rejects_missing_extra_and_false_terminals(self):
        raw=entry.server_source(entry.SOURCE,'c'*64)
        self.assertEqual(check(raw,'<complete ownership whole>'),0)
        namespace={'__name__':'pure_definitions_no_io'}
        exec(compile(raw,'<definitions>','exec'),namespace)
        good=[0,True,[],3896,562,1664]
        self.assertTrue(namespace['complete_result'](*good))
        for index,values in {0:[1,143,True,None],1:[False,None],2:[['failure'],None],
            3:[3814,3895,3897],4:[556,561,563],5:[1654,1663,1665]}.items():
            for value in values:
                args=good.copy();args[index]=value
                self.assertFalse(namespace['complete_result'](*args))
        self.assertIn(entry.SOURCE,raw);self.assertNotIn(entry.previous.SOURCE,raw)
        self.assertIn('PG5414',raw);self.assertNotIn('PG5128',raw)
        self.assertLess(raw.index('    format_preflight(args,'),raw.index("with (OUT / 'maven.private.log')"))
        self.assertIn('format-before-pt.safe.json',raw)

    def test_source_gates_and_all_four_readonly_files_remain_explicit(self):
        raw=inspect.getsource(entry.main)
        self.assertEqual(len(entry.READONLY),4)
        for literal in ("result['tests']==1164","result['suites']==137","result['phaseExits']==[0,0]",
            "proof['physicalMain']!=767","value['missed']","'tests': 3896, 'suites': 562, 'mainClasses': 1664"):
            self.assertIn(literal,raw)
        for path in (entry.__file__,__file__):self.assertEqual(checkPath(path),0)


if __name__=='__main__':unittest.main()
