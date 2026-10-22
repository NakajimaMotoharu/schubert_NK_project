"""Original4203/4209 actual counters and six TestID joins; not effort or formal acceptance."""
import hashlib
import json
import os
from pg5940_private_lock_compile import ROOT,BASE,sha
from pg6864_original4209_artifacts import read_whole
from pg6818_current_counter_delta import closed,counters
from pg6092_current3985_static_join import source_case_candidates

BEFORE=BASE/'PG6828-current4203-cases/qualification.json'
BEFORE_SHA='87d3de1b887514b10838d3cef748e9421f17574c87ae89a37f5b616a8e1f4dc0'
WEB='web:dev/codex/schubert/nk/web/bootstrap/WebManagementServer.class'
ACCEPTOR='batch:dev/codex/schubert/nk/batch/mq/ArtemisAcceptorReadinessClient.class'
PG='batch:dev/codex/schubert/nk/batch/file/MorningGateEvidence.class'


def compare(before,after):
    if set(before['allPhysicalMainSha256'])!=set(after['allPhysicalMainSha256']):raise ValueError('same all1669 physical keys')
    if closed(after)-closed(before)!={ACCEPTOR}or closed(before)-closed(after):raise ValueError('only acceptor newly four-closed, no reopened class')
    changed={k for k in before['allPhysicalMainSha256']if before['allPhysicalMainSha256'][k]!=after['allPhysicalMainSha256'][k]}
    if changed!={WEB}:raise ValueError('one Web Main physical difference')
    rows=[dict(physicalClass=k,before=before['allActualClassCounters'].get(k),after=after['allActualClassCounters'].get(k))
      for k in sorted(set(before['allActualClassCounters'])|set(after['allActualClassCounters']))if before['allActualClassCounters'].get(k)!=after['allActualClassCounters'].get(k)]
    if {r['physicalClass']for r in rows}!={WEB,ACCEPTOR,PG}:raise ValueError('unrelated original counter change requires independent classification')
    return dict(explicitFourClosedBefore=len(closed(before)),explicitFourClosedAfter=len(closed(after)),newlyClosedClasses=[ACCEPTOR],
      reopenedClasses=[],changedCounters=rows,moduleCountersBefore=counters(before),moduleCountersAfter=counters(after))


def test_id_trace(cases):
    mapping={
      'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/mq/AcceptorObjectBoundaryTest.java':{
        'opsMqObj001RejectsEachNonObjectExtraPropsBeforeStartedRead':'PT-OPS-MQ-OBJ001',
        'opsMqObj002RejectsEachNonObjectParamsBeforeStartedRead':'PT-OPS-MQ-OBJ002'},
      'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/PostgresObservationRowsTest.java':{
        'pgRows001MaximumFullGoldenAndOversizeOrSameBomRankGapRejected':'PT-OPS-PG-ROWS-001'},
      'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/bootstrap/WebManagementDeadlineTest.java':{
        'webMgmt335001ZeroBudgetDoesNotWaitForOtherCloseOwner':'PT-WEB-MGMT335001',
        'webMgmt335002InterruptDuringLockReturnsUnknownWithNotification':'PT-WEB-MGMT335002',
        'webMgmt335003PreInterruptDuringStartContentionRefusesLatePromotion':'PT-WEB-MGMT335003'}}
    result=[]
    for path,names in mapping.items():
        p=ROOT/path;cls=path.split('/src/test/java/')[1][:-5].replace('/','.')
        for method,tid in names.items():
            digest=hashlib.sha256(source_case_candidates(p.read_text(),method)[0].encode()).hexdigest()
            found=[c for c in cases if c['class']==cls and c['caseNameSha256']==digest]
            if len(found)!=1:raise ValueError('one original current XML case per independent TestID')
            result.append(dict(testId=tid,sourcePath=path,sourceSha256=sha(p),method=method,originalCase=found[0]))
    if len(result)!=6:raise ValueError('six JUnit methods, no vector inflation')
    return result


def main():
    qp,q,cases=read_whole()
    if sha(BEFORE)!=BEFORE_SHA:raise ValueError('frozen genuine previous4203')
    before=json.loads(BEFORE.read_bytes())
    if(before['tests'],q['tests'])!=(4203,4209):raise ValueError('two original full results, no PASS addition')
    value=dict(actualExit=0,source=q['productionSource'],currentQualificationSha256=sha(qp),priorQualificationSha256=BEFORE_SHA,**compare(before,q),
      independentTestIdTrace=test_id_trace(cases),testsExecuted=0,wholeReplayed=False,formalAccepted=False,acceptedLeafDelta=0,effortPercent=None,
      physicalClassDenominator=1669,absentCounterSynthesized=False,vmActions=0,ptAlternativeCompleted=0,
      toolSha256=sha(ROOT/'tools/quality/pg6874_current_counter_delta.py'),scope='ACTUAL_COUNTERS_NOT_EFFORT; one Web class byte change, every other Main byte exact')
    out=BASE/'PG6874-current-counter-delta-v1';os.umask(0o077);out.mkdir();p=out/'manifest.json'
    with p.open('x')as f:json.dump(value,f,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0,manifestSha256=sha(p),newlyClosed=1,closedBefore=value['explicitFourClosedBefore'],closedAfter=value['explicitFourClosedAfter'])))


if __name__=='__main__':main()
