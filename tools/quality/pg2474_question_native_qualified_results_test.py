import json
from pathlib import Path
import unittest
from pyflakes.api import check
from pg1446_current_cold_stage import W
import pg2474_question_native_qualified_results as q


class InputResult(unittest.TestCase):
    def test_actual_unique_result_and_no_input_or_unknown_result_exclusion(self):
        a=Path(q.ARTIFACT).read_bytes();b=Path(q.BASELINE).read_bytes()
        r=json.loads((W/'pg2470-chr-a01-native-v1.safe.json').read_bytes())
        for paths in [[],[q.ARTIFACT]]:q.result_changes(paths,a,b,r)
        for paths in [[q.ARTIFACT,q.ARTIFACT],[q.BASELINE],['program/characterization/reports/foreign.json'],
                      ['program/characterization/tests/resources/cases/dif-allowlist.json'],['src/foreign.java'],['pom.xml'],['.mvn/foreign'],None]:
            with self.assertRaises(ValueError):q.result_changes(paths,a,b,r)
        for aa,bb in [(b'foreign',b),(a,b'foreign'),(None,b)]:
            with self.assertRaises(ValueError):q.result_changes([q.ARTIFACT],aa,bb,r)
        for key,bad in [('productionSource','3b7f3567b54f91f3a9dbeb859e8dd77e8353a2c8'),('actualExit',1),('actualExit',False),
                        ('sameCapturedParentApiWebCaddyBeforeAfter',False),('rawCookieTokenExported',True),('sharedCurrentDriver',None),
                        ('fullGate',True),('baselineSha256','0'*64),('harnessClassesSha256','0'*64)]:
            with self.assertRaises(ValueError):q.result_changes([q.ARTIFACT],a,b,{**r,key:bad})

    def test_whole_server_transport_current_full_crc_and_latest_only(self):
        self.assertEqual(q.server(),q.entry().__globals__['CODE'])
        for text in ['PG2474-native-v1','source-full-PG2404','runs/PG2404-six-v1',q.SOURCE,'3637','len(streams)==9','NativePointDominance']:
            self.assertTrue(text in q.server(),text)
        for text in ['pg2466-question-current-native-catalog-v1','pg2474-question-current-native-qualified-v1','pg2405-question-jdbc-full-qualified-v1']:
            self.assertTrue(text in q.source(),text)
        self.assertEqual(0,check(Path(q.__file__).read_text(),q.__file__))


if __name__=='__main__':unittest.main()
