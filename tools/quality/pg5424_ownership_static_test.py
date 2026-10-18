import inspect
import unittest
from pyflakes.api import check,checkPath
import pg5424_ownership_static as entry


class CurrentStatic(unittest.TestCase):
    def test_fixed_whole_and_current_readonly_gates_precede_any_diagnostic(self):
        raw=inspect.getsource(entry.main)
        for literal in ("qualified['result']['tests']!=3896","qualified['result']['mainClasses']!=1664",
            "review['readonlyCandidateCount']!=4","'includeCheckstyle':False"):
            self.assertIn(literal,raw)
        self.assertLess(raw.index("review['actualExit']"),raw.index('out.mkdir'))
        for path in (entry.__file__,__file__):self.assertEqual(checkPath(path),0)

    def test_original_rules_and_auxiliary_abi_are_kept_without_f03_acceptance(self):
        data={'source':entry.SOURCE,'head':entry.SOURCE,'candidateJob':'PG5424-ownership-static-input-v1',
            'staticJob':'PG5424-ownership-static-v1','includeCheckstyle':False,'qualifiedJars':{},
            'originalStaticManifestSha256':'a'*64,'priorStaticManifestSha256':'b'*64,'sourceSha256':{}}
        raw=entry.server_source(data)
        self.assertEqual(check(raw,'<current static standalone>'),0)
        self.assertIn('source-full-PG5414',raw);self.assertNotIn('source-full-PG4968',raw)
        self.assertIn('runs/PG4976-ssc304-static-v1/manifest.safe.json',raw)
        self.assertIn('3896/1664',raw);self.assertIn('F03Accepted=False',raw)
        self.assertNotIn('PG4696 original PG4694',raw);self.assertNotIn('PG4420 independently',raw)
        self.assertIn('Checkstyle',raw)
        with self.assertRaises(ValueError):entry.server_source(dict(data,includeCheckstyle=True))


if __name__=='__main__':unittest.main()
