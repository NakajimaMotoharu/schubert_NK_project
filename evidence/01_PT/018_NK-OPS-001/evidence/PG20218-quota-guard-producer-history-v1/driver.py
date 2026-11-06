"""Independent metadata-only regression: never invokes Product, API, VM or event writers."""
import copy,json,pathlib,unittest,sys,hashlib,datetime,re
import pmo_quota_binding as q
NOW='2026-11-06T02:00:00+00:00';TERMINAL='2026-11-06T01:59:00+00:00'
BEFORE={'primary':{'usedPercent':27,'resetsAt':1794395640,'windowDurationMins':10080},'secondary':None}
def observation(used=28):
 return q.receipt({'ordinaryUsageAllowed':True,'rateLimits':{'primary':{'usedPercent':used,'resetsAt':1794395640,'windowDurationMins':10080},'secondary':None}},NOW)
def bind(value,before=BEFORE,now=NOW,terminal=TERMINAL,cap=6):return q.end_fields(before,value,q.digest(value),now,terminal,cap)
class EndQuotaCases(unittest.TestCase):
 def test_fresh_post_terminal_increment_is_shared_not_tokens(self):
  v=bind(observation());self.assertEqual(1,v['observedSharedPp']);self.assertTrue(v['sameQuotaWindow']);self.assertIsNone(v['actualAllocatedPp']);self.assertIsNone(v['tokenTotals']);self.assertEqual('UNKNOWN',v['attribution'])
 def test_original_bug_pre_terminal_observation_rejects(self):
  v=observation();v['observedAtUTC']='2026-11-06T01:58:59+00:00'
  with self.assertRaisesRegex(ValueError,'follow the actual terminal'):bind(v,now='2026-11-06T01:59:01+00:00')
 def test_stale_future_and_changed_receipt_reject(self):
  for instant in ['2026-11-06T01:57:59+00:00','2026-11-06T02:00:01+00:00']:
   v=observation();v['observedAtUTC']=instant
   with self.assertRaisesRegex(ValueError,'within120s'):bind(v)
  v=observation();wrong=q.digest(v);v['ordinaryUsageAllowed']=False
  with self.assertRaisesRegex(ValueError,'immutable'):q.end_fields(BEFORE,v,wrong,NOW,TERMINAL,6)
 def test_reserve_boundary_saves_end_but_prevents_new_work(self):
  for used in [90,95,100]:
   v=bind(observation(used));self.assertFalse(v['newImplementationAllowedByQuota']);self.assertEqual(used-27,v['observedSharedPp']);self.assertTrue(v['postTerminalReceiptVerified'])
  self.assertTrue(bind(observation(89))['newImplementationAllowedByQuota'])
 def test_unavailable_or_denied_quota_is_preserved_not_zero(self):
  v=observation();v['primary']=None;v['ordinaryUsageAllowed']=None;a=bind(v);self.assertIsNone(a['observedSharedPp']);self.assertFalse(a['newImplementationAllowedByQuota']);self.assertTrue(a['missingOrChangedWindowIsNotZero'])
  v=observation();v['ordinaryUsageAllowed']=False;self.assertFalse(bind(v)['newImplementationAllowedByQuota'])
 def test_reset_window_is_not_subtracted(self):
  v=observation(1);v['primary']['resetsAt']=1795000000;a=bind(v);self.assertFalse(a['sameQuotaWindow']);self.assertIsNone(a['observedSharedPp']);self.assertIsNone(a['actualAllocatedPp'])
 def test_decreasing_same_window_rejects_and_cap_overrun_records(self):
  with self.assertRaisesRegex(ValueError,'cannot decrease'):bind(observation(26))
  a=bind(observation(35));self.assertEqual(8,a['observedSharedPp']);self.assertTrue(a['groupCapExceeded']);self.assertTrue(a['newImplementationAllowedByQuota'])
  for cap in [None,True,0,11,float('nan')]:
   with self.assertRaisesRegex(ValueError,'group cap'):bind(observation(),cap=cap)
 def test_available_secondary_window_also_preserves_ten_percent(self):
  v=observation();v['secondary']=q.window({'usedPercent':90,'resetsAt':1793930400,'windowDurationMins':300});a=bind(v);self.assertFalse(a['newImplementationAllowedByQuota']);self.assertEqual(1,a['observedSharedPp'])
if __name__=='__main__':
 slot=sys.argv[1] if len(sys.argv)==2 else 'pg20218-quota-end-guard-v1';assert len(sys.argv)<=2 and re.fullmatch(r'pg[0-9]+-quota-end-guard-v[0-9]+',slot)
 suite=unittest.defaultTestLoader.loadTestsFromTestCase(EndQuotaCases);out=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')/slot;assert not out.exists();out.mkdir()
 with (out/'unittest.safe.txt').open('w') as f:result=unittest.TextTestRunner(stream=f,verbosity=2).run(suite)
 assert result.testsRun==8 and not result.skipped
 p=pathlib.Path(q.__file__);m=dict(actualExit=0 if result.wasSuccessful() else 1,tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),skipped=len(result.skipped),testDomain='QUALITY_TOOL_METADATA_NOT_PRODUCTION_PT',productTests=0,apiRequests=0,modelQuotaOrResetMutated=False,driverSha256=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),targetPath=str(p),targetSha256=hashlib.sha256(p.read_bytes()).hexdigest(),reportSha256=hashlib.sha256((out/'unittest.safe.txt').read_bytes()).hexdigest(),atJST=datetime.datetime.now().astimezone().isoformat());(out/'manifest.safe.json').write_text(json.dumps(m,indent=2)+'\n');print(json.dumps(m));sys.exit(m['actualExit'])
