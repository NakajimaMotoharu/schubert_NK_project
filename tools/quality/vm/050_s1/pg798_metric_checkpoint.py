"""487 existing group checkpoint; missing token/individual allocation stays null."""
import datetime
import json
import os
from pathlib import Path
import subprocess
T=Path(__file__).resolve().parents[4]
M=Path('/home/mini/codex/project1/work/PMO/pgpt-execution-metrics/events.jsonl')

if __name__=='__main__':
    last=json.loads(M.read_bytes().splitlines()[-1]);assert last['eventId']=='PGPT-20261008-0205'
    e=json.loads(json.dumps(last));e.update(eventId='PGPT-20261008-0206',previousEventId=last['eventId'],eventType='CHECKPOINT',timeJST=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(),gitHead=subprocess.check_output(['git','rev-parse','HEAD'],cwd=T,text=True).strip(),run='PG796/797-v4/798-probe',quotaAfter={'fetchedAtJST':'2026-10-09T18:55:13+09:00','limitId':'codex','windowDurationMins':10080,'resetsAt':1791987599,'usedPercent':69,'remainingPercent':31,'source':'get_usage_limits'},observedSharedPp=1,sameQuotaWindow=True,tokenMeasurementIds=['e9eae571cf297bc9c4381631728158e024ba72b9861cd09f8df1fb137cd3b38b'],tokenCoverageNote='NO_NEW_EXPLICIT_USAGE_RECORD N/T null; shared68->69 not individual PGPT/PMO/review allocation',actualPaths=['796 signed source102/187/SQL28/history29','797v4stage0/verify0 87s no business mutation','798stage0/verify0 86.990672s no business mutation'],failureIds=['BUG936','BUG942','BUG943','BUG944','BUG945'],attemptResult='798_NATIVE_LIMITED_NORMAL_RETURN',elapsedSeconds=86.990672,externalJobWaitSeconds=None,timeOverlapNote='798 actual verify wall only; model-active/external-wait split unmeasured',unaccepted=['798 independent full原値/resource0/maximum-gap extraction','source102 pending codeonly/new genuine/native','BUG927 true cause/global100/CHR/formal/handover'],retryCause='797 failed compile/role/assembly slots preserved; 798 wholepair/synchronousgap/unreachable stop surface corrected fresh without Production rebuild',nextCommand='fresh independent800 full post; frozen current750 -> signed796 pending codeonly799 -> fresh same9de2 one-use resume/genuine')
    e['acceptedDelta']={'closedIds':[],'reopenedIds':[],'criteriaSatisfied':['798 whole pair sameowner bounded wait and lost-body retain noSQL independent faults','798 actual75s bothservers/new scopes normal narrowly'],'evidenceRefs':['602_PG794_795_796_当source全6・署名候補結果.md']}
    with M.open('ab')as f:f.write((json.dumps(e,ensure_ascii=False)+'\n').encode());f.flush();os.fsync(f.fileno())
    print(json.dumps({'eventId':e['eventId'],'individualAllocatedPp':None,'N':None,'T':None}))
