"""Compare genuine original counters, not effort or formal acceptance; no PT replay."""
import hashlib
import json
import os
from pathlib import Path
from pg5940_private_lock_compile import ROOT,BASE,sha
from pg6804_original4202_artifacts import read_whole

BEFORE=BASE/'PG6768-current4197-cases/qualification.json'
BEFORE_SHA='b4b22a3e1d8d2c1d0a433c0fb3fa3fb2a77c9aed795cd56e64c8f5947d7122e9'
INTERMEDIATE=BASE/'PG6784-current4197-cases/qualification.json'
INTERMEDIATE_SHA='0e7d0f359c06b1fa33a3352cc38c63304a9cdd3d284884530f29a100bf7d8fe4'
KINDS=('LINE','METHOD','CLASS','BRANCH')
TARGETS={'web:dev/codex/schubert/nk/web/bootstrap/WebManagementServer.class',
 'batch:dev/codex/schubert/nk/batch/file/StartupLaunchRecord.class',
 'batch:dev/codex/schubert/nk/batch/platform/CleanupWorkerRequest$Expiry.class',
 'batch:dev/codex/schubert/nk/batch/platform/CleanupFailedBackupRequest.class'}


def explicit_four100(c):
    return all(k in c and type(c[k].get('missed'))is int and c[k]['missed']==0 and type(c[k].get('covered'))is int and c[k]['covered']>0 for k in KINDS)


def closed(q):return {k for k,c in q['allActualClassCounters'].items()if explicit_four100(c)}


def counters(q):
    return {kind:{field:sum(m['coverage'][kind][field]for m in q['modules'].values())for field in('covered','missed')}for kind in KINDS}


def compare(before,after):
    if set(before['allPhysicalMainSha256'])!=set(after['allPhysicalMainSha256']):raise ValueError('same complete physical class keys, no silent class deletion')
    new=closed(after)-closed(before);lost=closed(before)-closed(after)
    if new!=TARGETS or lost:raise ValueError('only the four qualified target closures, no hidden reopening')
    physical={k for k in before['allPhysicalMainSha256']if before['allPhysicalMainSha256'][k]!=after['allPhysicalMainSha256'][k]}
    if physical!={'web:dev/codex/schubert/nk/web/bootstrap/WebManagementServer.class'}:raise ValueError('one necessary Main change only')
    changes=[]
    for key in sorted(set(before['allActualClassCounters'])|set(after['allActualClassCounters'])):
        a=before['allActualClassCounters'].get(key);b=after['allActualClassCounters'].get(key)
        if a!=b:changes.append(dict(physicalClass=key,mainBytesChanged=key in physical,before=a,after=b))
    if {x['physicalClass']for x in changes}!=TARGETS:raise ValueError('unrelated actual counter difference needs independent classification')
    return dict(explicitFourClosedBefore=len(closed(before)),explicitFourClosedAfter=len(closed(after)),
      newlyClosedClasses=sorted(new),reopenedClasses=sorted(lost),changedCounters=changes,
      moduleCountersBefore=counters(before),moduleCountersAfter=counters(after))


def test_id_trace(cases):
    mapping={
      'StartupLaunchBoundaryTest':{'launchBoundary001PositiveDelAndNonemptyFinalRowAreRejected':'PT-CORR-LAUNCH-001'},
      'ExpiryRequestBoundaryTest':{'expiryBoundary001EachPreviouslyUnverifiedConstructorIdentityRejects':'PT-CORR-EREQ-001','expiryBoundary002DelAndSameLengthProfileTailRejectAndEraseOwnedBytes':'PT-CORR-EREQ-002'},
      'FailedProfileBoundaryTest':{'failedBoundary001DelAndSameRowCountTailRejectAndEraseOwnedBytes':'PT-CORR-CFREQ-001','failedBoundary002InternallyValidPairFromDifferentRunCannotMatchOuterClaim':'PT-CORR-CFREQ-002'}}
    result=[]
    from pg6092_current3985_static_join import source_case_candidates
    for short,names in mapping.items():
        paths=list(ROOT.glob('src/*/src/test/java/**/'+short+'.java'))
        if len(paths)!=1:raise ValueError('one independent Test source')
        p=paths[0];text=p.read_text();fqcn=p.as_posix().split('/src/test/java/')[1][:-5].replace('/','.')
        for method,test_id in names.items():
            digest=hashlib.sha256(source_case_candidates(text,method)[0].encode()).hexdigest()
            found=[c for c in cases if c['class']==fqcn and c['caseNameSha256']==digest]
            if len(found)!=1:raise ValueError('one actual original XML case per independent TestID/method')
            result.append(dict(testId=test_id,sourcePath=p.relative_to(ROOT).as_posix(),sourceSha256=sha(p),method=method,originalCase=found[0]))
    return result


def main():
    qp,q,cases=read_whole()
    if sha(BEFORE)!=BEFORE_SHA or sha(INTERMEDIATE)!=INTERMEDIATE_SHA:raise ValueError('frozen genuine historical original measurements')
    before,middle=[json.loads(p.read_bytes())for p in(BEFORE,INTERMEDIATE)]
    if (before['tests'],middle['tests'],q['tests'])!=(4197,4197,4202):raise ValueError('three actual source runs, never arithmetic PASS addition')
    value=dict(actualExit=0,source=q['productionSource'],currentQualificationSha256=sha(qp),priorQualificationSha256=BEFORE_SHA,
      intermediateQualificationSha256=INTERMEDIATE_SHA,**compare(before,q),intermediateModuleCounters=counters(middle),
      independentTestIdTrace=test_id_trace(cases),testsExecuted=0,wholeReplayed=False,formalAccepted=False,
      acceptedLeafDelta=0,effortPercent=None,physicalClassDenominator=1669,absentCounterSynthesized=False,
      vmActions=0,ptAlternativeCompleted=0,toolSha256=sha(Path(__file__)),
      scope='ACTUAL_COUNTER_DELTA_NOT_EFFORT_RATE; fixed Main bytes except proven Web result protocol; source changes disclosed')
    out=BASE/'PG6818-current-counter-delta-v1';os.umask(0o077);out.mkdir();p=out/'manifest.json'
    with p.open('x')as f:json.dump(value,f,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0,manifestSha256=sha(p),newlyClosed=len(value['newlyClosedClasses']),closedBefore=value['explicitFourClosedBefore'],closedAfter=value['explicitFourClosedAfter'])))


if __name__=='__main__':main()
