"""Original API counter delta and one independent normal-Test join; not effort or acceptance."""
import hashlib
import json
import os
from pathlib import Path
from pg5940_private_lock_compile import ROOT,BASE,sha
from pg6830_original4203_artifacts import read_whole
from pg6818_current_counter_delta import closed,counters
from pg6092_current3985_static_join import source_case_candidates

BEFORE=BASE/'PG6802-current4202-cases/qualification.json'
BEFORE_SHA='ff93e636dca2c4f09fd3142375e751d8fd1b129ebf1c44e91165d33cc737d2c6'
TARGET='api:dev/codex/schubert/nk/api/bootstrap/ApiManagementServer.class'
TEST='src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/bootstrap/ApiManagementDefaultBindTest.java'
METHOD='apiMgmt001DefaultBindUsesFixedLoopbackAndOwnedReadinessLifecycle'


def compare(before,after):
    if set(before['allPhysicalMainSha256'])!=set(after['allPhysicalMainSha256']):raise ValueError('all physical keys retained')
    if closed(after)-closed(before)!={TARGET}or closed(before)-closed(after):raise ValueError('only API newly closed, no reopened class')
    changed={k for k in before['allPhysicalMainSha256']if before['allPhysicalMainSha256'][k]!=after['allPhysicalMainSha256'][k]}
    if changed!={TARGET}:raise ValueError('only API Main physical difference')
    rowchanges=[dict(physicalClass=k,before=before['allActualClassCounters'].get(k),after=after['allActualClassCounters'].get(k))
      for k in sorted(set(before['allActualClassCounters'])|set(after['allActualClassCounters']))if before['allActualClassCounters'].get(k)!=after['allActualClassCounters'].get(k)]
    if {r['physicalClass']for r in rowchanges}!={TARGET}:raise ValueError('unrelated counter change needs independent classification')
    return dict(explicitFourClosedBefore=len(closed(before)),explicitFourClosedAfter=len(closed(after)),newlyClosedClasses=[TARGET],
      reopenedClasses=[],changedCounters=rowchanges,moduleCountersBefore=counters(before),moduleCountersAfter=counters(after))


def main():
    qp,q,cases=read_whole()
    if sha(BEFORE)!=BEFORE_SHA:raise ValueError('frozen genuine prior4202 original')
    before=json.loads(BEFORE.read_bytes())
    if(before['tests'],q['tests'])!=(4202,4203):raise ValueError('two actual full runs, no PASS arithmetic')
    path=ROOT/TEST;fqcn=TEST.split('/src/test/java/')[1][:-5].replace('/','.')
    digest=hashlib.sha256(source_case_candidates(path.read_text(),METHOD)[0].encode()).hexdigest()
    found=[c for c in cases if c['class']==fqcn and c['caseNameSha256']==digest]
    if len(found)!=1:raise ValueError('one current original XML case for default-bind independent TestID')
    value=dict(actualExit=0,source=q['productionSource'],currentQualificationSha256=sha(qp),priorQualificationSha256=BEFORE_SHA,**compare(before,q),
      independentTestIdTrace=dict(testId='PT-API-MGMT-NORM-001',sourcePath=TEST,sourceSha256=sha(path),method=METHOD,originalCase=found[0]),
      testsExecuted=0,wholeReplayed=False,formalAccepted=False,acceptedLeafDelta=0,effortPercent=None,
      physicalClassDenominator=1669,absentCounterSynthesized=False,vmActions=0,ptAlternativeCompleted=0,
      toolSha256=sha(Path(__file__)),scope='ACTUAL_COUNTERS_NOT_EFFORT; API source difference disclosed, every other Main byte exact')
    out=BASE/'PG6840-api-counter-delta-v1';os.umask(0o077);out.mkdir();p=out/'manifest.json'
    with p.open('x')as f:json.dump(value,f,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0,manifestSha256=sha(p),newlyClosed=1,closedBefore=value['explicitFourClosedBefore'],closedAfter=value['explicitFourClosedAfter'])))


if __name__=='__main__':main()
