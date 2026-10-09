"""487 checkpoint of failed v1/owned handoff/current v2 preflight; no acceptance credit."""
import datetime,json,os,subprocess
from pathlib import Path
M=Path('/home/mini/codex/project1/work/PMO/pgpt-execution-metrics/events.jsonl')
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
def main():
 last=json.loads(M.read_bytes().splitlines()[-1]);assert last['eventId']=='PGPT-20261008-0232'
 for n in ('pg896-handoff-execute-v1','pg897-bootstrap-before-v1','pg894-compile-v2','pg894-oracle-v2','pg894-stage-v2','pg898-bootstrap-import-v1'):
  assert(W/(n+'.exit')).read_bytes()==b'0\n'
 assert(W/'pg894-verify-v1.exit').read_bytes()==b'143\n'
 e=json.loads(json.dumps(last));e.update(eventId='PGPT-20261008-0233',previousEventId=last['eventId'],eventType='CHECKPOINT',timeJST=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(),gitHead=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),run='PG894v1/896/897/894v2compile-stage/898',attemptResult='V1_FAILED143_PRESERVED_OWNED_HANDOFF0_V2_GUEST_IMPORT0_VERIFY_ONGOING',failureIds=['BUG-991'],retryCause='Unused transitive local import absent; fixed whole generated closure/explicit re/directory naming/new-only v2. Original verify143 not normalized. Current capture DB0, M/A held then authenticated pidfd TERM8960/allresources0.',actualPaths=['896 full895 unchanged/owned fixed Java pidfd TERM once0/4.674156s','897 fresh full24/full32/signed187/65native/current source/allresources0/2.6494s/exact895SHA','894v2 current862 wholeABI-Werror and argument oracle0; stage0','898 actual guest eleven module imports/hash0400/boot identity0/0.28239s before M/A/DB/Ref'],quotaBefore=last['quotaAfter'],quotaAfter={'fetchedAtJST':'2026-10-10T05:12:00+09:00','limitId':'codex','windowDurationMins':10080,'resetsAt':1791987599,'usedPercent':83,'remainingPercent':17,'source':'get_usage_limits; minute precision only'},observedSharedPp=1,tokenMeasurementIds=['94bb7f90f0785ae69993d9c996ddf2e5842289f672687bad30cfd4e4a1222d16'],tokenCoverageNote='N/T=null NO_NEW_EXPLICIT_USAGE_RECORD; shared82-to83 not attributable PGPT/PMO/individual WBS; no token conversion.',elapsedSeconds=None,externalJobWaitSeconds=None,timeOverlapNote='Per-command elapsed preserved separately; failed v1 wall and model/wait split not summed or inferred.',workCategory='NATIVE_CONNECTION',nextCommand='Attach issued894v2 verify tool; only after normal0 execute once, independent current full post/native; no stage/handoff/start replay')
 with M.open('ab')as f:f.write((json.dumps(e,ensure_ascii=False)+'\n').encode());f.flush();os.fsync(f.fileno())
 print(json.dumps({'eventId':e['eventId'],'acceptedDelta':0,'N':None,'T':None,'allocatedPp':None}))
if __name__=='__main__':main()
