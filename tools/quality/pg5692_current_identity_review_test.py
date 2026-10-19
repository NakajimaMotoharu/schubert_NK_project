"""Exact current diagnostic identity join and refusal vectors; no PMD suppression."""
import copy
import json
import unittest
from pyflakes.api import checkPath
import pg5690_current_identity_review as target


def fixtures():
    original=json.loads((target.BASE/'PG5594-current-jdbc-review-v1/manifest.json').read_bytes())
    facts=json.loads((target.W/'pg5689-current-identity-facts-v1/manifest.safe.json').read_bytes())
    path=target.BASE/'PG5588-current3905-cases/qualification.json'
    return original,facts,json.loads(path.read_bytes()),json.loads(path.with_name('cases.json').read_bytes())


class Identity(unittest.TestCase):
    def test_exact_thirty_of_sixtyfive_not_blanket_equality_exemption(self):
        original,facts,whole,cases=fixtures();before=copy.deepcopy(original)
        rows,counts=target.assess(original,facts,whole,cases)
        self.assertEqual(before,original);self.assertEqual(1647,len(rows));self.assertEqual(30,counts['individualSelfSuppressionGuards'])
        self.assertEqual(35,len(counts['otherEqualityStillUnreviewed']))
        for r in rows:
            if r['rule']=='CompareObjectsWithEquals'and r['sourcePath'].endswith(('UserMutationReplayService.java','ApiProcessLifetime.java')):self.assertEqual('NOT_REVIEWED',r['status'])
            if 'typedSelfSuppressionFact'in r:self.assertTrue(r['rawWarningRetained']);self.assertTrue(r['wholeCaseRefs']);self.assertTrue(r['currentPhysicalClasses'])

    def test_foreign_bool_bad_whole_or_actual_class_never_reuses_evidence(self):
        original,facts,whole,cases=fixtures()
        for key,value in(('source','f'*40),('actualExit',False),('helperSha256','0'*64),('fixtureSha256','0'*64)):
            with self.assertRaises(ValueError):target.assess(original,{**facts,key:value},whole,cases)
        for key,value in(('tests',3896),('mainClasses',1650),('FESFlakyNotRun',1)):
            with self.assertRaises(ValueError):target.assess(original,facts,{**whole,key:value},cases)
        bad=copy.deepcopy(facts);bad['identity']['physicalMainSha256'].pop(next(iter(bad['identity']['physicalMainSha256'])))
        with self.assertRaises(ValueError):target.assess(original,bad,whole,cases)

    def test_unknown_ambiguous_or_shifted_span_cannot_qualify(self):
        original,facts,whole,cases=fixtures()
        bad=copy.deepcopy(facts);bad['rows'][0]['kind']='GENERIC_IDENTITY'
        with self.assertRaises(ValueError):target.assess(original,bad,whole,cases)
        bad=copy.deepcopy(facts);bad['rows'].append(copy.deepcopy(bad['rows'][0]))
        with self.assertRaises(ValueError):target.assess(original,bad,whole,cases)
        bad=copy.deepcopy(facts);bad['rows'][0]['lastColumn']=str(int(bad['rows'][0]['lastColumn'])+1)
        with self.assertRaises(ValueError):target.assess(original,bad,whole,cases)
        bad=copy.deepcopy(original)
        row=next(r for r in bad['findings']if r['rule']=='CompareObjectsWithEquals'and r['sourcePath']==facts['rows'][0]['path']and r['beginline']==facts['rows'][0]['firstLine']);row['sourceSha256']='0'*64
        with self.assertRaises(ValueError):target.assess(bad,facts,whole,cases)

    def test_original_case_failure_and_static_inputs(self):
        original,facts,whole,cases=fixtures();bad=copy.deepcopy(cases)
        for c in bad:
            if c['class'].endswith('.ApiBrokerContextsTest'):c['result']='FAILED'
        with self.assertRaises(ValueError):target.assess(original,facts,whole,bad)
        self.assertEqual(0,checkPath(target.__file__));self.assertEqual(0,checkPath(__file__))


if __name__=='__main__':unittest.main()
