"""487 single writer checkpoint; shared quota is not individually allocated token cost."""
import datetime
import json
import os
from pathlib import Path
import subprocess
T = Path(__file__).resolve().parents[4]
M = Path('/home/mini/codex/project1/work/PMO/pgpt-execution-metrics/events.jsonl')
if __name__ == '__main__':
    last = json.loads(M.read_bytes().splitlines()[-1])
    assert last['eventId'] == 'PGPT-20261008-0213'
    e = json.loads(json.dumps(last))
    e.update(eventId='PGPT-20261008-0214', previousEventId=last['eventId'],
             eventType='CHECKPOINT', timeJST=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(),
             gitHead=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=T, text=True).strip(),
             run='PG818/819 failures -> PG820 notstarted',
             quotaAfter={'fetchedAtJST':'2026-10-09T22:10:44+09:00', 'limitId':'codex',
                         'windowDurationMins':10080, 'resetsAt':1791987599,
                         'usedPercent':72, 'remainingPercent':28, 'source':'usage tool + clock'},
             observedSharedPp=1, sameQuotaWindow=True, tokenMeasurementIds=['bbc21bd116be0e77b12773ac4bee1fdf6d9796fdf18e94a3a034c8eb0fd213a5'],
             tokenCoverageNote='N/T null NO_NEW_EXPLICIT_USAGE_RECORD; shared71->72 is not PGPT/PMO/review allocated cost',
             actualPaths=['813 current796 owned recovery0; 815 actual runtime retirement0; 816 full24/554/43/resources0 retained; no replay'],
             attemptResult='818 format refusal;819 NullAway compile refusal; PT notrun, candidate undeployed',
             failureIds=['BUG949','BUG952','BUG953','BUG954','BUG955','BUG956'],
             retryCause='Beforefix registers: C NUL boundary, unique noactivation, credential EUID, Service ControlGroup, internal unbounded handshake/multiRPC. Explicit RPC original budget correction, independent delay oracle. NullAway first negative compile corrected without suppression',
             workCategory='IMPLEMENTATION', elapsedSeconds=None, externalJobWaitSeconds=None,
             timeOverlapNote='No actual model-active/wait split measured; old1800 failure preserved',
             unaccepted=['SSC239 candidate selected/static/native/whole regression/main design publication',
                         'BUG949 causal proof/genuine parent/native', 'global100/CHR/formal/handover'],
             nextCommand='freeze corrected candidate hashes and selected820 fresh slot; independent native comparison -> designonlymain -> required fresh full -> signed new source codeonly -> separate once resume/genuine/native')
    e['acceptedDelta']={'closedIds':[], 'reopenedIds':[], 'criteriaSatisfied':[], 'evidenceRefs':[]}
    with M.open('ab') as out:
        out.write((json.dumps(e, ensure_ascii=False)+'\n').encode()); out.flush(); os.fsync(out.fileno())
    print(json.dumps({'eventId':e['eventId'], 'N':None, 'T':None, 'actualAllocatedPp':None}))
