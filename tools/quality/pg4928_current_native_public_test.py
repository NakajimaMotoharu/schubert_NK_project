import unittest
import xml.etree.ElementTree as E
from pyflakes.api import checkPath
import pg4928_current_native_public as role


class Projection(unittest.TestCase):
    def test_exact_current_counts_and_historical_only17_no_automatic_acceptance(self):
        raw=role.source()
        for text in ('3761','551','1647','pg4926-current-native-qualified-v1','pg4846-ssc301-302-whole-qualified-v1','PG4926-native-v1',"'PMDRaw': 1655","'CheckstyleRaw': 0","'source': '7fffab57a567914956b66452e5e54388642efdec'","'currentSourceCriteriaRevalidationPending': True","'effortPercent': None","'formalAccepted': False"):
            self.assertIn(text,raw)
        self.assertEqual(0,checkPath(role.__file__));self.assertEqual(0,checkPath(__file__))

    def test_session_redaction_changes_no_counters_or_class_method_line_semantics(self):
        base=role.previous.previous.base
        raw=b'<report name="fixture"><sessioninfo id="synthetic-only" start="12" dump="34"/><package name="p"><class name="C"><method name="m" desc="()V" line="7"/></class></package>'
        raw+=b''.join(('<counter type="'+k+'" missed="1" covered="2"/>').encode()for k in ('LINE','METHOD','CLASS','BRANCH','INSTRUCTION','COMPLEXITY'))+b'</report>'
        expected={k:{'missed':1,'covered':2}for k in base.COUNTERS};expected.update(classByteMismatch=0,formal=False)
        public,proof=base.redact_report(raw,expected)
        self.assertNotIn(b'id="synthetic-only"',public);self.assertEqual(base.semantic_report(E.fromstring(raw)),base.semantic_report(E.fromstring(public)))
        self.assertEqual(6,len(E.fromstring(public).findall('counter')));self.assertTrue(proof['counterContentUnchanged'])
        with self.assertRaises(ValueError):base.redact_report(raw,{**expected,'LINE':{'missed':0,'covered':3}})


if __name__=='__main__':unittest.main()
