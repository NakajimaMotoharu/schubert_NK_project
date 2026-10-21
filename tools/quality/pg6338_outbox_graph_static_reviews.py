"""Forty-four individually located current ordinary Outbox spans; no raw suppression."""
import json
import os
from pathlib import Path
from collections import Counter
from pg5940_private_lock_compile import ROOT,W,BASE,sha
from pg6326_web_graph_qualification import original_source
from pg5958_private_lock_reason_review import fragment
from pg6292_standalone_interrupt_context import rule_premise
from static_disposition_overlay import load,apply_decisions

PLAN=BASE/'PG6336-current4048-static-plan-v1/manifest.json'
PLAN_SHA='e02d77526918eddda08c78fe895ef9c1cbf81bd946f45c7ded3f7694dade15a1'
G='AvoidCatchingGenericException';S='AvoidSynchronizedStatement';E='CompareObjectsWithEquals'
T='DoNotUseThreads';V='AvoidUsingVolatile';I='AvoidInstanceofChecksInCatchClause'
SPEC={
 'OutboxDispatcher':{
 (51,G):(1,'Ordinary Runtime/typed send failure is inspected for fatal cause/suppressed/linked/next before markFailure. Direct Error is not caught. Independent322002/003 assert no mark for nested Error and exact normal retry SQL afterconditions; failure code is not proof of successful send.'),
 (75,G):(1,'Claim SQL/RTE failure attempts existing rollback and rethrows before owned TWR close. Fatal graph retained by TWR is classified at the actual owned worker boundary, not called successful claim. The graph change does not alter transaction or rollback policy.'),
 (88,G):(1,'markSent SQL/RTE failure rolls back and rethrows; neither computed marked boolean nor JMS success bypasses commit/owned close. Nested cleanup fatal is not authorized as another worker cycle. This is not a guarantee of actual vendor recovery.'),
 (102,G):(1,'markFailure SQL/RTE failure attempts rollback and rethrows; the durable attempt/backoff transition must commit normally before return. Fatal classification cannot issue an extra mark or create a success receipt.'),
 (114,G):(2,'Both unchecked setup spans guard an acquired but unreturned Connection. Exactly one closeAfterSetupFailure runs before failure propagation; original fatal and nonfatal-over-fatal cleanup follow unchanged SS320, with no JDBC lease or JMS work issued during failed setup.'),
 (123,G):(2,'Both unchecked close-secondary spans use the existing distinct/fatal severity combiner and never retry the close. The factory retains original identity or promoted cleanup Error; graph inspection adds no I/O or suppression mutation.'),
 (158,G):(2,'Both unchecked rollback-secondary spans retain the existing SS320 severity policy. A failed rollback is not confirmed successful transaction or permission to mark/send again. The owned worker subsequently distinguishes any fatal retained in a nonfatal graph.'),
 (169,E):(1,'Throwable reference inequality is deliberate: identical provider objects must not self-suppress and equals does not express failure identity. Fatal/nonfatal precedence and one cleanup invocation remain separately verified.')},
 'OwnedOutboxDispatcher':{
 (16,T):(1,'Standalone SS311/324/342 process owns this exact background thread handle, not an injected J2EE container-managed thread. Field ownership is not current VM/process ownership evidence.'),
 (25,T):(1,'The dedicated non-daemon dispatcher is constructed before start and starts only through its exact owner; ordinary HTTP request threads do not send. This standalone JavaSE owner contract is outside the pinned J2EE managed-thread prohibition, not authority to launch a real Root.'),
 (43,S):(1,'Private lock serializes start with stopping and started publication; this/class/caller monitor is not borrowed. No claim occurs before the exact owner starts its prepared thread.'),
 (51,S):(1,'wake checks started/stopping/failed and publishes signalled under the same private lock as the wait. No provider object or lease is exposed under this monitor.'),
 (60,S):(1,'healthy snapshots started/stopping/failed under the same private monitor as state changes. It is local worker health, not external readiness or proof of physical cleanup.'),
 (68,S):(1,'The worker waits and consumes signalled under the same private monitor, then releases it before DB/JMS dispatch. Stop notifications cannot be lost across the two stopping checks.'),
 (77,G):(1,'SQL/RTE from actual dispatch is examined for fatal graph before any later retry. Error escapes to the enclosing fatal branch; only Error-free ordinary infrastructure failure retains the existing periodic cycle. No raw provider text is emitted.'),
 (84,T):(1,'Restoring this exact worker interrupt after wait failure is a standalone JavaSE interruption contract, not container thread creation. The following private-lock state update makes the owner unhealthy.'),
 (85,S):(1,'Interrupted worker marks failed and notifies under the same private monitor as wake/healthy. The owner still joins before dependencies may be released; no external resource close is inferred.'),
 (89,G):(1,'Direct/promoted Error marks this worker failed before rethrow to its fixed uncaught diagnostic. It is never converted to ordinary SQL retry or a committed outbox result. Arbitrary failing provider diagnostic getters and real VM OOM remain residual risks.'),
 (90,S):(1,'Fatal failed-state publication and notification use the same private lock as all health observers. This synchronized scope does not perform DB/JMS I/O or close outer dependencies.'),
 (100,T):(1,'Current caller thread identity is observed solely to reject owner self-join in this standalone process. It neither starts another thread nor proves actual native/Unit stop.'),
 (100,E):(1,'Thread reference identity is required for self-join rejection; equals is not the ownership predicate. The branch precedes stop publication and join of the exact worker.'),
 (102,S):(1,'close publishes stopping and notify under the private lock, then releases it before joining. Concurrent provider dispatch can finish without needing an externally held caller monitor.'),
 (114,T):(1,'Only the closing caller interrupt flag is restored after the exact worker has been joined, preserving existing shutdown behavior. Pinned J2EE managed-thread premise does not apply to this standalone owner observation.')},
 'WebLogDispatcher':{
 (93,G):(1,'Transaction work/commit SQL/RTE failure is retained as primary and triggers one existing rollback before rethrow and owned finally close. The ordinary failure graph boundary is separate; this review does not replace existing Web JDBC compound precedence with API SS320 ordering.'),
 (97,G):(1,'Rollback RTE is retained only as a distinct secondary on the original failure. It cannot turn a failed transaction into a successful projected log or durable retry mark.'),
 (98,E):(1,'Same provider Throwable must not be added to itself. Reference identity is the suppression contract and must not invoke provider equals.'),
 (99,G):(1,'Rollback Error remains fatal and retains the distinct nonfatal transaction failure. It does not authorize another rollback, mark or JMS send.'),
 (105,G):(2,'Both outer unchecked spans retain primary through owned Connection finally even for setup failure. No not-yet-acquired connection is closed; normal return still requires commit and close. This is the existing Web owner boundary, not physical DB release certification.'),
 (117,G):(2,'Both unchecked Connection.close spans use the unchanged Web compound contract. A distinct close Error remains fatal and retains primary; other distinct close failures stay secondary. The new graph inspection does not silently rewrite the established Web fatal-primary ranking.'),
 (119,I):(1,'Close Error severity must be distinguished from ordinary SQL/RTE cleanup to prevent nonfatal retry normalization. This type predicate implements the established Web owner contract, not an external success or cleanup confirmation.'),
 (119,E):(1,'A close Error identical to primary cannot suppress itself. Distinct close Error retains the original through existing Web priority; identity is not semantic equals.'),
 (123,E):(1,'Non-promoted cleanup is added only for a distinct Throwable. Same Error/RTE remains itself; no provider equals, repeated close or new failure-code work is introduced.')},
 'WebLogReplayWorker':{
 (21,T):(1,'Standalone SS311/324 JavaSE Web runtime retains its exact dedicated replay handle, not a J2EE-managed pool thread. A saved handle is not current native ownership proof.'),
 (26,V):(1,'The immutable lastReport reference is published by the worker and read by snapshot callers without a common lock; volatile visibility is required. Atomic cycle counters do not make every independent reference read a safely published replacement, and aggregate snapshot is not a transaction receipt.'),
 (41,T):(1,'Prepared daemon platform thread has one outer owner and fixed terminal handler, then starts only through the factory. The standalone off-HTTP replay contract is outside the pinned J2EE prohibition; real runtime thread permission/termination is not certified here.'),
 (70,G):(1,'SQL/RTE is inspected through the dedicated full provider graph before failedCycles increments. Fatal graph terminates with no completed/failed ordinary cycle; Error-free failures preserve schedule/backoff and redacted aggregate metrics. General session catalog behavior is not widened.'),
 (107,T):(1,'Current caller identity is observed only to reject joining the same worker in standalone bounded close. It is neither a thread launch nor proof of an actual Root owner.'),
 (107,E):(1,'Reference equality compares caller with the exact retained thread for self-join safety; value equality would not express ownership. A failed self-join is not a clean stop.'),
 (114,T):(1,'Caught join interruption restores only the caller interrupt before fixed unconfirmed-stop exception. The standalone owner still requires a genuine join; pinned J2EE managed-thread restriction is not the execution context.')}
}
TESTS={
 'OutboxDispatcher':['dev.codex.schubert.nk.api.messaging.outbound.OutboxDispatcherTest','dev.codex.schubert.nk.api.messaging.outbound.OutboxFailureOwnershipTest'],
 'OwnedOutboxDispatcher':['dev.codex.schubert.nk.api.messaging.outbound.OwnedOutboxDispatcherTest'],
 'WebLogDispatcher':['dev.codex.schubert.nk.web.logging.WebLogDispatcherTest'],
 'WebLogReplayWorker':['dev.codex.schubert.nk.web.logging.WebLogReplayWorkerTest']}


def calculate():
    source=original_source();rows=load(PLAN,PLAN_SHA,source);rule=rule_premise()
    poms={}
    for module in ('api','web'):
        path=ROOT/('src/schubert-nk-'+module+'/pom.xml');text=path.read_text()
        if any(t in text for t in ('<packaging>war','<packaging>ear','jakarta.ejb')):raise ValueError('standalone owned-worker context must be rereviewed')
        poms[module]=sha(path)
    qp=BASE/'PG6326-web-graph-qualification-v1/manifest.json';q=json.loads(qp.read_bytes())
    private=W/'pg6326-web-graph-qualification-v1/manifest.safe.json'
    if sha(qp)!='e8e0961898824f64eb493a18995ca9f8ddb27be84a1805314fac703426a426bf'or sha(private)!=q['privateManifestSha256']:raise ValueError('original current89/all8511667/static proof')
    proof=json.loads(private.read_bytes());found=Counter();decisions=[];snapshot=W/'pg6324-web-graph-selected-v1/source'
    for row in rows:
        name=Path(row['sourcePath']).stem;key=(int(row['beginline']),row['rule'])
        if name not in SPEC or key not in SPEC[name]:continue
        count,reason=SPEC[name][key];found[(name,key)]+=1;path=ROOT/row['sourcePath']
        if row['status']!='NOT_REVIEWED_CURRENT_SOURCE'or sha(path)!=row['sourceSha256']or sha(path)!=proof['allSourceHashes'][row['sourcePath']]:raise ValueError('one exact unreviewed current source span')
        module=row['sourcePath'].split('/')[1].removeprefix('schubert-nk-')
        prefix=module+':'+row['sourcePath'].split('/src/main/java/')[1][:-5]
        family={k:v for k,v in proof['allPhysicalMainSha256'].items()if k==prefix+'.class'or k.startswith(prefix+'$')}
        if not family:raise ValueError('actual original owner family')
        context=row['rule']==T;declarations=[]
        if not context:
            for cls in TESTS[name]:
                rel=Path('src/schubert-nk-'+module+'/src/test/java')/(cls.replace('.','/')+'.java');test=ROOT/rel
                if not test.is_file()or sha(test)!=sha(snapshot/rel):raise ValueError('unchanged actual89 semantic Test source')
                declarations.append(dict(className=cls,sourceSha256=sha(test)))
        value=dict(row,source=source,status='CONTEXT_NOT_APPLICABLE'if context else'REQUIRED_CONTRACT',
            reason='1355 current ordinary Outbox source applicability: '+reason,diagnosticFragment=fragment(path.read_text(),row),
            rawWarningRetained=True,owningPhysicalClassHashes=family,plannedCurrentWholeCaseClasses=declarations,
            currentWholeCaseRefs=[],currentWholeJoinPending=True,staticContextPremiseOnly=context,
            actualRuntimeProven=False,formalAccepted=False,F03Accepted=False,ptAlternativeCompleted=0,
            reviewScope='PINNED_STANDALONE_RULE_PREMISE_ONLY'if context else'APPLICABILITY_ONLY_NOT_RUNTIME_OR_COVERAGE_ACCEPTANCE')
        if context:value.update(pinnedRule=rule,standaloneModulePomSha256=poms[module])
        decisions.append(value)
    if found!=Counter({(n,k):v[0]for n,sites in SPEC.items()for k,v in sites.items()})or len(decisions)!=44:raise ValueError('all44 exact span multiplicities')
    updated=apply_decisions(rows,decisions)
    return decisions,dict(actualExit=0,source=source,baseManifestPath=PLAN.relative_to(ROOT).as_posix(),baseManifestSha256=PLAN_SHA,
        rawFindings=1356,statusCounts=dict(Counter(r['status']for r in updated)),reviewed=44,pmdRawRemoved=0,
        pinnedRule=rule,standaloneModulePomSha256=poms,testsExecuted=0,currentWholeJoinPending=True,
        newAcceptedLeaves=0,formalAccepted=False,F03Accepted=False,ptAlternativeCompleted=0,effortPercent=None,
        unresolved=['original4048 case binding pending','all14 prior missing semantic refs remain unresolved','other343/global/F03/native/CHR/451/actual runtime separate'])


def main():
    rows,value=calculate();os.umask(0o077);out=BASE/'PG6338-outbox-graph-static-review-v1';out.mkdir()
    with(out/'decisions.json').open('x')as f:json.dump(rows,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    value['decisionsSha256']=sha(out/'decisions.json')
    with(out/'manifest.json').open('x')as f:json.dump(value,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0,reviewed=44,statusCounts=value['statusCounts'],manifestSha256=sha(out/'manifest.json'))))


if __name__=='__main__':main()
