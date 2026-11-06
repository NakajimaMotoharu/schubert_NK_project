"""BUG2331/YKT2076 metadata regression. Reads public evidence only; no product execution."""
from pathlib import Path
import hashlib,json,unittest,datetime,io,sys
from pmo_event_summary import unit_pass_summary,declared_test_count,matches_verified_count
R=Path.cwd();EVENTS=R.parent/'PMO/pgpt-execution-metrics/events.jsonl';rows=[json.loads(x) for x in EVENTS.read_text().splitlines()];byid={x['eventId']:x for x in rows};OUT=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG20416-event-summary-count-guard-v1';assert not OUT.exists();joins=[];sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def manifest_for(event):
    refs=event['sourceEvidenceRefs'];assert len(refs)==1
    p=R/refs[0]['path'];p.resolve().relative_to((R/'evidence/01_PT').resolve());assert not p.is_symlink() and p.name=='manifest.json';assert sha(p)==refs[0]['sha256']
    m=json.loads(p.read_text());assert m['actualExit']==0 and all(m[k]==0 for k in ['failures','errors','skipped','aborted']);return m


class Checks(unittest.TestCase):
    def test_literal_summaries(self):
        for count,expected in [(1,'ALL1_PASS_FOUR100_POST0'),(8,'ALL8_PASS_FOUR100_POST0'),(9,'ALL9_PASS_FOUR100_POST0'),(13,'ALL13_PASS_FOUR100_POST0'),(16,'ALL16_PASS_FOUR100_POST0')]:
            self.assertEqual(expected,unit_pass_summary(count))

    def test_invalid_counts(self):
        for value in [0,-1,None,True,'13',13.0]:
            with self.assertRaises(ValueError):unit_pass_summary(value)
            with self.assertRaises(ValueError):matches_verified_count('ALL13_PASS_FOUR100_POST0',value)

    def test_unknown_and_ambiguous_summaries(self):
        for label in [None,'PASS','ALL0_PASS_FOUR100_POST0','ALL013_PASS_FOUR100_POST0','ALL13_PASS_RESOURCE8_PASS','ALL9_PASS_ALL9_PASS']:
            self.assertIsNone(declared_test_count(label));self.assertFalse(matches_verified_count(label,13))
        self.assertEqual(14,declared_test_count('CORRECTED_NORMAL_FIXTURE_ALL14_PASS_FOUR100_POST0'))
        self.assertEqual(12,declared_test_count('RESOURCE12_PASS_19DOM_INDEPENDENT_POST0'))

    def test_original_mismatch_and_append_correction(self):
        original=byid['PGPT-20261008-4002'];m=manifest_for(original);self.assertEqual(13,m['tests'])
        self.assertEqual('ALL8_PASS_FOUR100_POST0',original['attemptResult']);self.assertFalse(matches_verified_count(original['attemptResult'],m['tests']))
        correction=byid['PGPT-20261008-4004'];self.assertEqual(original['eventId'],correction['correctsEventId'])
        self.assertEqual('ALL13_PASS_FOUR100_POST0',correction['correctedValue']);self.assertTrue(matches_verified_count(correction['correctedValue'],m['tests']))
        self.assertEqual(0,correction['additionalProductionTests']);self.assertIsNone(correction['observedSharedPp'])

    def test_latest_csrf_summary_uses_nine(self):
        event=byid['PGPT-20261008-4005'];m=manifest_for(event);self.assertEqual(9,m['tests'])
        self.assertEqual('ALL9_PASS_FOUR100_POST0',event['attemptResult']);self.assertTrue(matches_verified_count(event['attemptResult'],m['tests']))

    def test_eight_recent_public_manifest_joins(self):
        expected={'PGPT-20261008-'+x for x in ['3989','3991','3994','3996','3998','4000','4002','4005']}
        ends=[e for e in rows if e.get('eventType')=='GROUP_END' and e['eventId'] in expected];self.assertEqual(8,len(ends))
        for event in ends:
            m=manifest_for(event);summary=byid['PGPT-20261008-4004']['correctedValue'] if event['eventId']=='PGPT-20261008-4002' else event['attemptResult']
            self.assertTrue(matches_verified_count(summary,m['tests']));joins.append(dict(eventId=event['eventId'],manifest=event['sourceEvidenceRefs'][0],verifiedTests=m['tests'],originalSummary=event['attemptResult'],effectiveSummary=summary,matched=True))

    def test_generation_from_actual_independent_counts(self):
        for event_id,expected in [('PGPT-20261008-4002','ALL13_PASS_FOUR100_POST0'),('PGPT-20261008-4005','ALL9_PASS_FOUR100_POST0')]:
            self.assertEqual(expected,unit_pass_summary(manifest_for(byid[event_id])['tests']))


OUT.mkdir();stream=io.StringIO();result=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Checks));(OUT/'checks.stdout').write_text(stream.getvalue());code=0 if result.wasSuccessful() else 1
value=dict(actualExit=code,atJST=datetime.datetime.now().astimezone().isoformat(),metadataTests=result.testsRun,failures=len(result.failures),errors=len(result.errors),skipped=len(result.skipped),productionTests=0,sourceProofDelta=0,acceptedDelta=0,unitReexecuted=False,helper=dict(path='tools/quality/pmo_event_summary.py',sha256=sha(R/'tools/quality/pmo_event_summary.py')),driver=dict(path=str(Path(__file__).resolve().relative_to(R)),sha256=sha(__file__)),publicJoins=joins,oldEventAndEvidenceUnchanged=True,noEventWrites=True,noProductionOrVmOrPrivateAccess=True,bug='BUG-2331',horizontal='YKT-2076',files={'checks.stdout':sha(OUT/'checks.stdout')});(OUT/'manifest.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=code,metadataTests=result.testsRun,failures=len(result.failures),errors=len(result.errors),manifestSha256=sha(OUT/'manifest.json'))));sys.exit(code)
