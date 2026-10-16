"""Only technical session redaction; counters/class/method/line unchanged and no acceptance lift."""
import unittest
import xml.etree.ElementTree as ET
from pyflakes.api import checkPath
import pg4812_new_current_native_public_projection as target


class PublicNative(unittest.TestCase):
    def test_projection_exact_new_counts_and_historical_acceptance_only(self):
        raw=target.source()
        for literal in ['3739','549','1646','pg4782-new-current-native-qualified-v1','pg4696-ssc299-whole-qualified-v1','PG4782-native-v1']:
            self.assertIn(literal,raw)
        self.assertIn("'currentSourceCriteriaRevalidationPending': True",raw)
        self.assertIn("'effortPercent': None",raw);self.assertIn("'formalAccepted': False",raw)
        self.assertIn("'PMDRaw': 1654",raw);self.assertIn("'CheckstyleRaw': 0",raw)
        self.assertEqual(0,checkPath(target.__file__))

    def test_literal_six_counters_and_all_non_session_bytes_preserved(self):
        base=target.previous.base
        raw=b'<report name="fixture"><sessioninfo id="synthetic-only" start="12" dump="34"/><package name="p"><class name="C"><method name="m" desc="()V" line="7"/></class></package>'
        raw+=b''.join(('<counter type="'+k+'" missed="1" covered="2"/>').encode()for k in ['LINE','METHOD','CLASS','BRANCH','INSTRUCTION','COMPLEXITY'])+b'</report>'
        expected={k:{'missed':1,'covered':2}for k in base.COUNTERS};expected.update(classByteMismatch=0,formal=False)
        public,proof=base.redact_report(raw,expected)
        self.assertNotIn(b'id="synthetic-only"',public)
        self.assertEqual(base.semantic_report(ET.fromstring(raw)),base.semantic_report(ET.fromstring(public)))
        self.assertEqual(6,len(ET.fromstring(public).findall('counter')));self.assertTrue(proof['counterContentUnchanged'])
        with self.assertRaises(ValueError):base.redact_report(raw,{**expected,'LINE':{'missed':0,'covered':3}})


if __name__=='__main__':unittest.main()
