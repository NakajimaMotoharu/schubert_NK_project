"""Twenty-six current Outbox source spans, individually reviewed after SS320 PG."""
import json
import os
from pathlib import Path
from collections import Counter
from pg5940_private_lock_compile import ROOT,W,BASE,sha
from pg6268_outbox_failure_qualification import original_source
from pg5958_private_lock_reason_review import fragment
from static_disposition_overlay import load,apply_decisions

PLAN=BASE/'PG6278-current4040-static-plan-v1/manifest.json'
PLAN_SHA='e4286667281a591231e17d7426f4c8c36afb674bb3bf2495b32fe73b6b5ed2a8'
G='AvoidCatchingGenericException'
I='AvoidInstanceofChecksInCatchClause'
E='CompareObjectsWithEquals'
SPEC={
 'OutboxJmsSender':{
 (38,G):(1,'Factory RTE becomes fixed typed unconfirmed send failure before ownership is acquired. A null context is rejected; no stage/commit/close is invented when open did not return.'),
 (48,G):(1,'Stage checked JMS/RTE triggers one rollback attempt and typed unconfirmed failure. It cannot run commit or mark SENT on this branch; rollback RTE is retained rather than duplicate confirmation.'),
 (54,G):(1,'Commit RTE permits duplicate confirmation only through the explicit cause/linked identity graph, never suppressed rollback/close. Other outcomes remain typed unconfirmed. No retry/business duplication is introduced.'),
 (63,G):(1,'Unexpected provider RTE is wrapped once with the fixed lifecycle diagnostic. finally owns one close and SS320 prevents a cleanup Error from being converted to this nonfatal wrapper.'),
 (67,G):(1,'Direct provider Error is retained and rethrown by identity. finally closes once; original Error outranks another cleanup Error and distinct cleanup is suppressed, not retried as ordinary send failure.'),
 (79,G):(2,'Both overlapping close RTE/Error spans are explicit owned finally handling. With no primary Error propagates/ordinary failure is typed. With primary, fatal cleanup supersedes only nonfatal primary; all other outcomes retain primary without self-suppression. Original6266 six independent compound cases and original6270 JVM review, not a general Throwable swallowing policy.'),
 (81,I):(1,'No-primary close Error must remain fatal and cannot become OutboxSendException. This type branch does not infer close completion or a broker commit receipt.'),
 (85,I):(1,'Cleanup Error over non-Error primary is the SS320 fatal-priority contract. The fatal object cannot equal the nonfatal primary; primary is retained suppressed once before identical Error rethrow.'),
 (89,E):(1,'Throwable reference identity prevents self-suppression. equals can execute provider code and cannot represent identity of the original failure graph.'),
 (90,E):(1,'When typed OutboxSendException already wraps the same closing provider Throwable, do not attach that same cause again as suppressed. Identity, not semantic equality, preserves the existing graph.'),
 (128,G):(1,'Header codec RTE becomes fixed OutboxIntegrityException before JMS acquisition. Independent wire fixtures check UUID/length/layout; malformed bytes are not accepted or logged.'),
 (153,G):(1,'Payload constraint RTE becomes fixed integrity rejection before JMS acquisition, independent of transport duplicate confirmation. No raw payload or provider message is returned.'),
 (172,G):(1,'Secondary rollback RTE is suppressed on the original unconfirmed failure, never interpreted as confirmed commit. Error remains fatal; this helper does not catch Error or add a second rollback.'),
 (173,E):(1,'Original and rollback provider RTE may be the same object. Distinct-reference guard is required before addSuppressed; equals would not prevent self-suppression safely.')},
 'OutboxDispatcher':{
 (45,G):(1,'Only typed send failure or RTE enters durable failure accounting. markSent is after a normal sender return. SS320 cleanup Error now escapes this catch, as original6266 confirms, rather than manufacturing a retryable failure.'),
 (68,G):(1,'Claim SQL/RTE rolls back once then rethrows; returned connection is owned by TWR. Claim commit precedes JMS send. Unreturned setup is handled by the separate transaction ownership catch.'),
 (81,G):(1,'Short markSent SQL/RTE transaction rolls back once and rethrows. No transaction is held over JMS; failed commit/rollback is never a successful durable SENT receipt.'),
 (95,G):(1,'Short markFailure SQL/RTE transaction rolls back and rethrows rather than reporting committed retry state. Lease/backoff SQL is unchanged; cleanup cannot authorize another transaction.'),
 (107,G):(2,'Both RTE and Error setup spans retain the connection already returned by open. A failed setAutoCommit(false) closes it exactly once before rethrow, without claim/JMS/commit/rollback. SQL/RTE/Error setup matrix is original6266 FAIL320002/003; open failure itself has no acquired owner.'),
 (116,G):(2,'Both unchecked close-failure spans join SQL in the setup cleanup path. The pure retainFailure helper promotes secondary Error only above nonfatal primary; otherwise original identity stays, with distinct suppression. One close attempt, no replacement open.'),
 (128,G):(2,'Both unchecked rollback-failure spans join SQL in the one rollback helper. Fatal secondary escapes ordinary SQL/RTE retry, retaining primary; nonfatal secondary cannot erase primary. Outer TWR retains its existing one-close contract; no compensating commit/retry.'),
 (139,E):(1,'Primary and secondary Throwable may be the same reference. addSuppressed is legal only for distinct identity; value equality is neither equivalent nor safe on provider objects.')}
}


def calculate():
    source=original_source();rows=load(PLAN,PLAN_SHA,source)
    qp=BASE/'PG6268-outbox-failure-qualification-v1/manifest.json';q=json.loads(qp.read_bytes())
    private=W/'pg6268-outbox-failure-qualification-v1/manifest.safe.json';cp=private.with_name('cases.safe.json')
    order=BASE/'PG6270-outbox-failure-order-v2/manifest.json'
    if sha(qp)!='d4e587322de799db097dab934611431448b229953bae5838aa721b7c51ac0225'or sha(private)!=q['privateManifestSha256']or sha(cp)!=q['casesSha256']or sha(order)!='d62cfbef3d3d0bcccb4a4d45c58e252ca6783e2855ea6b5dacce1166dab30278':raise ValueError('original current51/allMain/static/JVM immutable')
    proof=json.loads(private.read_bytes());cases=json.loads(cp.read_bytes());found=Counter();decisions=[]
    refs=[r for r in cases if r['className'].endswith(('.OutboxFailureOwnershipTest','.OutboxDispatcherTest'))]
    if len(refs)!=25 or any(r['source']!=source or r['result']!='PASS_ORIGINAL_XML'for r in refs):raise ValueError('actual original six independent cases plus nineteen existing dispatcher cases')
    for row in rows:
        name=Path(row['sourcePath']).stem;key=(int(row['beginline']),row['rule'])
        if name not in SPEC:continue
        if key not in SPEC[name]:raise ValueError('every changed-owner diagnostic must be individually located')
        count,reason=SPEC[name][key];found[(name,key)]+=1;path=ROOT/row['sourcePath']
        if row['status']!='NOT_REVIEWED_CURRENT_SOURCE'or sha(path)!=row['sourceSha256']or sha(path)!=proof['allSourceHashes'][row['sourcePath']]:raise ValueError('current exact source, no duplicate disposition')
        prefix='api:'+row['sourcePath'].split('/src/main/java/')[1][:-5]
        family={k:v for k,v in proof['allPhysicalMainSha256'].items()if k==prefix+'.class'or k.startswith(prefix+'$')}
        if not family:raise ValueError('original owning class family including compiler helper')
        decisions.append(dict(row,source=source,status='REQUIRED_CONTRACT',reason='1338 individual SS320 current PG review: '+reason,
            diagnosticFragment=fragment(path.read_text(),row),rawWarningRetained=True,owningPhysicalClassHashes=family,
            originalSelectedCaseRefs=refs,qualificationSha256=sha(qp),jvmReviewSha256=sha(order),
            currentWholeCaseRefs=[],currentWholeJoinPending=True,actualRuntimeProven=False,
            formalAccepted=False,F03Accepted=False,ptAlternativeCompleted=0,
            reviewScope='APPLICABILITY_ONLY_NOT_GLOBAL_FUNCTIONAL_OR_COVERAGE_ACCEPTANCE'))
    if found!=Counter({(name,key):value[0]for name,sites in SPEC.items()for key,value in sites.items()})or len(decisions)!=26:raise ValueError('all26 actual spans/multiplicities')
    updated=apply_decisions(rows,decisions)
    return decisions,dict(actualExit=0,source=source,baseManifestPath=PLAN.relative_to(ROOT).as_posix(),baseManifestSha256=PLAN_SHA,
        rawFindings=1350,statusCounts=dict(Counter(r['status']for r in updated)),reviewed=26,pmdRawRemoved=0,
        currentWholeJoinPending=True,testsExecuted=0,newAcceptedLeaves=0,formalAccepted=False,F03Accepted=False,
        ptAlternativeCompleted=0,effortPercent=None)


def main():
    rows,value=calculate();os.umask(0o077);out=BASE/'PG6280-outbox320-static-review-v1';out.mkdir()
    with(out/'decisions.json').open('x')as f:json.dump(rows,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    value['decisionsSha256']=sha(out/'decisions.json')
    with(out/'manifest.json').open('x')as f:json.dump(value,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0,reviewed=26,statusCounts=value['statusCounts'],manifestSha256=sha(out/'manifest.json'))))


if __name__=='__main__':main()
