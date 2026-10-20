"""44 individual current-source applicability reviews, not full F03 or native acceptance."""
import json
import os
from collections import Counter
from pathlib import Path
from pg5940_private_lock_compile import ROOT,W,BASE,sha
from pg6208_keeper_faults_qualification import original_source
from pg5958_private_lock_reason_review import fragment
from static_disposition_overlay import load,apply_decisions,validate_rationales

PLAN=BASE/'PG6216-current4027-static-plan-v1/manifest.json'
PLAN_SHA='b5b463e333c714d9c0fea07e060a245f5774c6d97f26ca6a0b1613fab4862bb1'

# Source-specific sites were read independently; multiplicity retains both typed catch warnings.
CORE={
 (195,'AvoidCatchingGenericException'):(2,'REQUIRED_CONTRACT','ownedRelease intercepts IO/RTE/Error only at its owned release; finite observer returning still rethrows the same unconfirmed Throwable. Native fixed keeper cannot permit outer release. Null is rejected before callback, never converted to successful work.'),
 (225,'EmptyCatchBlock'):(1,'REQUIRED_CONTRACT','The only skipped action is failed fixed diagnostic output. Execution enters the same non-returning UNKNOWN observation loop; it does not claim resource release or retry work. Two diagnostic-fault children independently prohibit the outer marker.'),
 (225,'AvoidCatchingGenericException'):(2,'REQUIRED_CONTRACT','Diagnostic PrintStream RTE/Error must not replace the retained close failure and unwind downstream owners. The fixed diagnostic has no raw provider text; this catch only preserves UNKNOWN, with persistent VM availability risk explicit.'),
 (231,'AvoidCatchingGenericException'):(2,'REQUIRED_CONTRACT','Observation tick RTE/Error enters the prebuilt fixed monotonic fallback and then the same loop. Independent tick fault/IRQ child verifies elapsed lower bound; it is not automatic close, business resend or successful recovery.'),
 (234,'EmptyCatchBlock'):(1,'REQUIRED_CONTRACT','Fallback failure cannot authorize unwinding either. Its catch flows directly to the same UNKNOWN loop. Persistent wait/VM failure and CPU risk remain explicit, not converted to normal cleanup or a liveness guarantee.'),
 (234,'AvoidCatchingGenericException'):(2,'REQUIRED_CONTRACT','Both fallback RuntimeException and Error preserve the same isolation frame. Dedicated fallback children demonstrate no outer marker; actual VM crash survivability and low CPU under persistent VM failure are not claimed.'),
 (244,'DoNotUseThreads'):(1,'CONTEXT_NOT_APPLICABLE','Standalone JavaSE native retention thread clears preexisting IRQ before a private fixed-deadline fallback. This is not a Jakarta EE managed thread. It neither starts a thread nor transfers process ownership; UNKNOWN intentionally cannot return.'),
 (248,'DoNotUseThreads'):(1,'CONTEXT_NOT_APPLICABLE','The same standalone isolation thread clears a new IRQ after park so repeated interruption cannot collapse the remaining monotonic1000ms wait. No caller success or normal close is inferred from this local JMM/interrupt action.'),
 (255,'DoNotUseThreads'):(1,'CONTEXT_NOT_APPLICABLE','Fixed1000ms sleep is the normal observation interval of the standalone JavaSE UNKNOWN keeper, not a container-owned worker or business retry. No caller-supplied interval or new process is introduced.'),
 (256,'EmptyCatchBlock'):(1,'REQUIRED_CONTRACT','Interrupted sleep is only a notification: the enclosing UNKNOWN loop remains non-returning and retains outer ownership. Native keeper interruption is not a successful cleanup or new operation permit.')}
API={
 (34,'DoNotUseThreads'):(1,'CONTEXT_NOT_APPLICABLE','Private standalone management executor reference, not container-managed execution; no thread is allocated by this field declaration. Fixed owner prepares queue/state before HttpServer acquisition.'),
 (65,'AvoidCatchingGenericException'):(2,'REQUIRED_CONTRACT','Component start failure must attempt cleanup while retaining original RTE/Error primary. This is separate from native bind/registered owner entry. The eight compound bind316006 inputs verify primary/fatal priority and fixed redaction.'),
 (68,'AvoidCatchingGenericException'):(2,'REQUIRED_CONTRACT','Secondary cleanup RTE/Error is classified without replacing an Error primary with a nonfatal one. Only the preallocated fixed diagnostic may be suppressed; no raw secondary graph is published.'),
 (69,'AvoidInstanceofChecksInCatchClause'):(4,'REQUIRED_CONTRACT','The two exact Error type tests implement fatal-secondary priority only when primary is non-Error. PMD emits four overlapping spans for these two predicates; every raw span remains recorded. Polymorphic equality or a common Exception catch cannot implement the required fatal rule.'),
 (70,'CompareObjectsWithEquals'):(1,'REQUIRED_CONTRACT','Throwable reference identity prevents self-suppression; Throwable.equals is not the ownership/self relation. Only a distinct original failure receives the fixed prebuilt marker, as same-instance independent input verifies.'),
 (113,'DoNotUseThreads'):(1,'CONTEXT_NOT_APPLICABLE','Standalone loopback management HTTP owns one bounded ThreadPoolExecutor and32 queued tasks; it is not Jakarta EE container code. Prepared owner holds executor before bind, stop uses actual shutdown/join rather than daemon status as proof.'),
 (120,'DoNotUseThreads'):(1,'CONTEXT_NOT_APPLICABLE','The owned executor factory creates only its fixed-named daemon handler thread; normal stop still requires actual termination. This is standalone service process policy, not permission to manipulate unrelated threads.'),
 (213,'DoNotUseThreads'):(1,'CONTEXT_NOT_APPLICABLE','Entry interrupt is captured/temporarily cleared to test actual lock and executor termination within the same monotonic remaining budget, then restored in finally. No container thread assumption; this does not normalize an unconfirmed join.'),
 (219,'DoNotUseThreads'):(1,'CONTEXT_NOT_APPLICABLE','New interrupt during timed private stopLock acquisition is restored before fixed unconfirmed failure. It cannot set success caches or release downstream owners.'),
 (229,'DoNotUseThreads'):(1,'CONTEXT_NOT_APPLICABLE','shutdownNow targets only the private executor captured before bind; actual awaitTermination follows. Requesting shutdown is not completion, and no other executor/process is stopped.'),
 (231,'DoNotUseThreads'):(1,'CONTEXT_NOT_APPLICABLE','Actual owned executor join uses max(0, original deadline minus current nanoTime); zero remains finite. Timeout is unconfirmed, not normal close. Local independent stop cases cover this boundary, not actual Root stop.'),
 (235,'DoNotUseThreads'):(1,'CONTEXT_NOT_APPLICABLE','Join interrupt restores current thread flag and throws fixed unconfirmed failure; no closed success cache is written. It is standalone owner notification handling.'),
 (244,'DoNotUseThreads'):(1,'CONTEXT_NOT_APPLICABLE','Finally restores the preexisting interrupt on every exit after the explicit capture; it does not infer ownership or JVM/service termination.')}
WEB={
 (76,'AvoidUsingVolatile'):(1,'REQUIRED_CONTRACT','replies publishes one initialized consumer handle from serialized start to lock-free healthy(). Volatile supplies reference visibility only, not atomic multi-handle snapshots or runtime/native success.'),
 (77,'AvoidUsingVolatile'):(1,'REQUIRED_CONTRACT','replay publishes one initialized replay worker handle to lock-free healthy(); worker counters/state retain their own contracts. Replacing this with a plain field would remove its visibility edge.'),
 (78,'AvoidUsingVolatile'):(1,'REQUIRED_CONTRACT','retry worker handle is read by lock-free healthy() while start/close serialize separately. The volatile reference is required publication, not compound increment/collection mutation.'),
 (79,'AvoidUsingVolatile'):(1,'REQUIRED_CONTRACT','http handle is published by the synchronous owned callback and read by healthy(). Volatile preserves visibility outside ownerLock; no all-state atomic snapshot is promised.'),
 (80,'AvoidUsingVolatile'):(1,'REQUIRED_CONTRACT','management handle is read by lock-free ready(); its private volatile publication must remain even though startup and phase close use ownerLock. Four nonpublished handles were separately made plain; this one is not equivalent.'),
 (106,'AvoidSynchronizedStatement'):(1,'REQUIRED_CONTRACT','Private final ownerLock serializes one-shot startup and partial ownership stores against close. Lock is not this/class or caller input. This review does not claim bounded vendor start/close or actual native acceptance.'),
 (110,'CloseResource'):(1,'REQUIRED_CONTRACT','currentBroker aliases already-owned broker field, not an additional factory acquisition. Closing this local alias would invalidate later receive/session dependencies; reverse phase close owns the broker exactly after dependent roots/keys.'),
 (113,'CloseResource'):(1,'REQUIRED_CONTRACT','keys aliases already-owned codecs field; assembly borrows individual codecs, while reverse owned phase closes the field after callers drain. Local try-with-resources would prematurely erase active service keys.'),
 (118,'CloseResource'):(1,'REQUIRED_CONTRACT','transferRoot aliases the owned transfer field and is borrowed by LargeResultReader. Field phase close owns lifetime after HTTP/admission drain; no new directory is opened by this local nonnull alias.'),
 (124,'CloseResource'):(1,'REQUIRED_CONTRACT','assetRoot aliases the owned assets field and is borrowed by media resolution. The reverse close phase owns it; local alias cleanup would invalidate already-assembled file readers. Actual native inode/DB postconditions remain held.'),
 (211,'CloseResource'):(1,'REQUIRED_CONTRACT','control aliases already-captured management field before fallible start/promote. Registered field phase owns its cleanup even on startup failure; local successful-return cleanup must not stop the live management endpoint.'),
 (296,'AvoidSynchronizedStatement'):(1,'REQUIRED_CONTRACT','Same private final ownerLock protects ordered confirmed phases against concurrent start/close. WebRuntimeStop synchronously invokes but never stores Step[]; first unknown phase throws before later owners. This is not proof of real stop or resource postconditions.')}


def calculate():
    source=original_source();rows=load(PLAN,PLAN_SHA,source)
    qp=BASE/'PG6208-keeper-faults-qualification-v1/manifest.json';q=json.loads(qp.read_bytes())
    private=W/'pg6208-keeper-faults-qualification-v1/manifest.safe.json'
    if sha(qp)!='b000fbecefc854567332c21530dd63d1de411c06042f00d9e182e2def106ac34' or sha(private)!=q['privateManifestSha256']:
        raise ValueError('exact source63 actual compile/static/class proof')
    proof=json.loads(private.read_bytes());casepath=private.with_name('cases.safe.json')
    if sha(casepath)!=q['casesSha256']:raise ValueError('genuine selected case identity input')
    cases=json.loads(casepath.read_bytes());spec={'ServiceProcessResources':CORE,'ApiManagementServer':API,'WebNativeRuntime':WEB}
    found=Counter();decisions=[]
    for row in rows:
        name=Path(row['sourcePath']).stem;key=(int(row['beginline']),row['rule'])
        if name not in spec or key not in spec[name]:continue
        count,status,reason=spec[name][key];found[(name,key)]+=1
        path=ROOT/row['sourcePath']
        if sha(path)!=row['sourceSha256'] or sha(path)!=proof['allSourceHashes'][row['sourcePath']]:raise ValueError('exact current diagnostic/source')
        module=row['sourcePath'].split('/')[1].removeprefix('schubert-nk-');owner=module+':'+row['sourcePath'].split('/src/main/java/')[1][:-5]
        family={k:v for k,v in proof['allPhysicalMainSha256'].items() if k==owner+'.class' or k.startswith(owner+'$')}
        if not family:raise ValueError('actual original compiled owner family')
        testclass='dev.codex.schubert.nk.'+('api.file.ServiceResourceRetentionTest' if name=='ServiceProcessResources' else 'api.bootstrap.ApiManagement' if name=='ApiManagementServer' else 'web.bootstrap.WebNativeRuntimeTest')
        refs=[c for c in cases if c['className'].startswith(testclass)]
        if name!='WebNativeRuntime' and not refs:raise ValueError('actual relevant selected XML cases')
        decisions.append(dict(row,status=status,source=source,reason='1322 individual PG/source review: '+reason,
            diagnosticFragment=fragment(path.read_text(),row),rawWarningRetained=True,
            owningPhysicalClassHashes=family,originalSelectedCaseRefs=refs,
            qualificationSha256=sha(qp),currentWholeCaseRefs=[],currentWholeJoinPending=True,
            actualRuntimeProven=False,formalAccepted=False,F03Accepted=False,ptAlternativeCompleted=0,
            reviewScope='APPLICABILITY_ONLY_NOT_GLOBAL_FUNCTIONAL_OR_COVERAGE_ACCEPTANCE'))
    expected={(name,key):v[0] for name,sites in spec.items() for key,v in sites.items()}
    if found!=Counter(expected) or len(decisions)!=44:raise ValueError('all44 explicit current spans and multiplicities only')
    updated=apply_decisions(rows,decisions);validate_rationales(updated)
    value=dict(actualExit=0,source=source,baseManifestPath=PLAN.relative_to(ROOT).as_posix(),baseManifestSha256=PLAN_SHA,
        rawFindings=1340,statusCounts=dict(Counter(r['status'] for r in updated)),reviewed=44,newAcceptedLeaves=0,
        pmdRawRemoved=0,testsExecuted=0,currentWholeJoinPending=True,formalAccepted=False,F03Accepted=False,
        ptAlternativeCompleted=0,actualRuntimeProven=False,effortPercent=None,
        unresolved=['Core line246 AssignmentInOperand remains unclassified; prepare ordinary PG readability fix in next grouped source',
            'WebManagement unchecked compound startup cleanup remains BUG1561/YKT1318 OPEN; not classified here',
            'current whole/original artifact qualification/global100/native/CHR/451/trace remain separate'])
    return decisions,value


def main():
    rows,value=calculate();os.umask(0o077);out=BASE/'PG6218-keeper-static-review-v1';out.mkdir()
    with (out/'decisions.json').open('x') as f:
        json.dump(rows,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    value['decisionsSha256']=sha(out/'decisions.json')
    with (out/'manifest.json').open('x') as f:
        json.dump(value,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0,reviewed=44,statusCounts=value['statusCounts'],manifestSha256=sha(out/'manifest.json'))))


if __name__=='__main__':main()
