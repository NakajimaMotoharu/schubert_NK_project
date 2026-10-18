import inspect
import unittest
from pyflakes.api import check,checkPath
import pg5556_snapshot_static as entry


class SnapshotStatic(unittest.TestCase):
    def test_genuine_same_source_whole_precedes_any_new_output(self):
        raw=inspect.getsource(entry.main)
        self.assertLess(raw.index("q['tests']"),raw.index('out.mkdir'))
        self.assertIn('(3900,563,1664)',raw)
        self.assertIn("'wholeTestsReplayed':0",raw)
        for path in(entry.__file__,__file__):self.assertEqual(checkPath(path),0)

    def test_current_six_actual_jars_and_original_rules_remain(self):
        data={'source':entry.SOURCE,'head':entry.SOURCE,'candidateJob':'PG5556-snapshot-static-input-v1',
            'staticJob':'PG5556-snapshot-static-v1','includeCheckstyle':False,'qualifiedJars':{},
            'originalStaticManifestSha256':'a'*64,'priorStaticManifestSha256':'b'*64,'sourceSha256':{}}
        raw=entry.server_source(data)
        self.assertEqual(check(raw,'<new current standalone>'),0)
        self.assertIn('source-full-PG5550',raw);self.assertNotIn('source-full-PG5414',raw)
        self.assertIn('runs/PG5424-ownership-static-v1/manifest.safe.json',raw)
        self.assertIn('F03Accepted=False',raw);self.assertIn('current3900/1664',raw)
        self.assertIn('all current849 source bytes',raw)
        with self.assertRaises(ValueError):entry.server_source(dict(data,includeCheckstyle=True))


if __name__=='__main__':unittest.main()
