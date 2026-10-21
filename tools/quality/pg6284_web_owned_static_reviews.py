"""33 ordinary Web ownership/transaction applicability sites; startup compound gap excluded."""
import json
import os
from pathlib import Path
from collections import Counter
from pg5940_private_lock_compile import ROOT,W,BASE,sha
from pg6268_outbox_failure_qualification import original_source
from pg5958_private_lock_reason_review import fragment
from static_disposition_overlay import load,apply_decisions

PLAN=BASE/'PG6280-outbox320-static-review-v1/manifest.json'
PLAN_SHA='7cddd5464c75a46f6f6e72cf8455010e6c9d5a026fbb0db411568d4f6365a1f9'
G='AvoidCatchingGenericException';S='AvoidSynchronizedStatement';C='CloseResource'
SPEC={
 'WebHttpServer':{
 (112,C):(1,'The prepared WebHttpServer returned from construction retains the same Tomcat and MVC before vendor mutation. Explicit caller/native owner captures this wrapper before start; failed caller-less start destroys, while captured partial owner retains it for confirmed close. Existing component UNKNOWN/BUG1561 and actual native closure are not certified by this resource-transfer reason.'),
 (163,S):(1,'Successful vendor start publishes started under the same private lifecycleLock as port/mappedPaths/close. Caller-owned monitor or this/class lock is not used. This does not prove actual runtime readiness.'),
 (216,S):(1,'port reads closed/started and the actual connector under private lifecycleLock shared with close. It rejects unstarted/closed owners; a returned number is not a Root/native terminal receipt.'),
 (226,S):(1,'mappedPaths snapshots the actual MVC handler registry only while this started owner cannot be concurrently closed under lifecycleLock. Immutable copy escapes, not a mutable registry or held monitor.'),
 (240,S):(1,'close serializes this exact owner stop/destroy phases under lifecycleLock. stopped/destroyed are published only after their respective normal vendor returns; failed phases remain retryable UNKNOWN rather than fabricated completion. Socket/native release still requires separate evidence.')},
 'ReceiptReferenceRepository':{
 (48,G):(2,'Both unchecked insert-body spans retain primary across direct Statement finally close. Only verified three-column tuple is inserted with ON CONFLICT do nothing; close must succeed under the existing SQL/unknown precedence before the tuple read can proceed. No business UPDATE or API authorization is inferred.'),
 (97,G):(2,'Both unchecked row-body spans retain primary until owned ResultSet closes once. Missing/invalid/duplicate projection remains failure; borrowed Connection stays open for the enclosing transaction owner. Existing receipt unknown-primary/fixed-secondary contract is not replaced by API Outbox SS320 ranking.'),
 (107,G):(2,'Both unchecked statement-body spans protect the owned Statement, including failures from ResultSet cleanup. Finally closes once before Optional projection escapes. replace records only fixed diagnostics on unknown primary; this reason does not authorize raw provider logging.'),
 (131,G):(2,'Both unchecked work/commit spans attempt one rollback before propagating failed short transaction. A normally computed value cannot escape before commit and outer owned close. Fixed SQL vs unknown precedence follows RCPT005 compound fixtures, not ordinary retry success.'),
 (134,G):(2,'Both unchecked rollback-secondary spans use the established receipt replace policy. SQL+unknown promotes unknown; existing unknown primary retains identity plus new fixed ReceiptReferenceException. No failed rollback is a success receipt or additional work dispatch.'),
 (139,G):(2,'Both unchecked outer connection spans retain primary across direct owned finally close, including setup failure. Connection acquisition failure has no acquired owner. No JDBC transaction is held across IF030/JMS, and receipt locator never substitutes for API authorization.')},
 'RevocationRetryCoordinator':{
 (110,C):(1,'Nullable connection is the explicit owner state. After acquisition every body/setup outcome is captured, optional rollback runs once on failure, then same connection closes once before any result returns. Null/open failure has no acquired resource. This is not a TWR omission or ownership of the shared DataSource.'),
 (121,G):(2,'Both unchecked body/setup/commit spans retain failure to ensure rollback/close still execute. A result is withheld until cleanup. Final preserveFatal traverses the retained cause/suppressed identity graph before fixed RevocationRetryException, preventing direct/nested Error normalization.'),
 (127,G):(2,'Both unchecked rollback spans retain secondary via combine without self-suppression, then still attempt owned close. Failure graph is checked for Error afterward. This does not erase durable revoke rows or repeat business request publication.'),
 (134,G):(2,'Both unchecked close spans retain graph and withhold success; preserveFatal traverses cycles safely before fixed exception. Successful request result alone is not committed-and-closed success. Actual broker/VM revoke outcome is outside this source applicability check.')},
 'LocalLogoutHandler':{
 (42,G):(2,'Both unchecked terminal Logout spans attempt request display/security-context cleanup, preserve direct/nested fatal identity, then emit only fixed SessionStoreException. This does not bypass the existing authenticated POST/CSRF chain or manufacture durable revoke success.'),
 (66,G):(2,'Both unchecked durable enqueue/logout spans still invalidate the owned Servlet session once. It does not acquire a new session, redirect on failure, or treat failed enqueue as durable success; original graph proceeds through preserveFatal.'),
 (71,G):(2,'Both unchecked session-invalidation cleanup spans retain distinct secondary on original failure and then preserveFatal checks the full identity graph. A local cleanup failure cannot silently become Logout success; provider text is not exposed.'),
 (95,G):(2,'Both unchecked display-cleanup spans preserve original fatal graph when present and fatal secondary otherwise. Finally clears thread SecurityContext; a fixed session-store failure is not authentication success. This reason does not prove every third-party clear operation physically completed.'),
 (110,G):(1,'Session invalidation RTE is classified to fixed SessionStoreException only after nested Error preservation. Direct Error is not caught by this RTE clause and propagates through the outer cleanup path; no session is created as fallback.')}
}
TESTS={
 'WebHttpServer':['dev.codex.schubert.nk.web.bootstrap.WebHttpServerTest'],
 'ReceiptReferenceRepository':['dev.codex.schubert.nk.web.receipt.ReceiptReferenceRepositoryTest','dev.codex.schubert.nk.web.receipt.ReceiptReferenceFaultTest'],
 'RevocationRetryCoordinator':['dev.codex.schubert.nk.web.revocation.RevocationRetryCoordinatorTest'],
 'LocalLogoutHandler':['dev.codex.schubert.nk.web.session.LogoutControllerTest']}


def calculate():
    source=original_source();rows=load(PLAN,PLAN_SHA,source)
    qp=BASE/'PG6268-outbox-failure-qualification-v1/manifest.json';q=json.loads(qp.read_bytes())
    private=W/'pg6268-outbox-failure-qualification-v1/manifest.safe.json'
    if sha(qp)!='d4e587322de799db097dab934611431448b229953bae5838aa721b7c51ac0225'or sha(private)!=q['privateManifestSha256']:raise ValueError('all current original851/1667 and static inputs')
    proof=json.loads(private.read_bytes());found=Counter();decisions=[]
    for row in rows:
        name=Path(row['sourcePath']).stem;key=(int(row['beginline']),row['rule'])
        if name not in SPEC or key not in SPEC[name]:continue
        count,reason=SPEC[name][key];found[(name,key)]+=1;path=ROOT/row['sourcePath']
        if row['status']!='NOT_REVIEWED_CURRENT_SOURCE'or sha(path)!=row['sourceSha256']or sha(path)!=proof['allSourceHashes'][row['sourcePath']]:raise ValueError('one exact still-unreviewed current source span')
        prefix='web:'+row['sourcePath'].split('/src/main/java/')[1][:-5]
        family={k:v for k,v in proof['allPhysicalMainSha256'].items()if k==prefix+'.class'or k.startswith(prefix+'$')}
        if not family:raise ValueError('actual original owner class family')
        declarations=[]
        for cls in TESTS[name]:
            test=ROOT/'src/schubert-nk-web/src/test/java'/(cls.replace('.','/')+'.java')
            if not test.is_file():raise ValueError('explicit existing semantic Test source')
            declarations.append(dict(className=cls,sourceSha256=sha(test)))
        decisions.append(dict(row,source=source,status='REQUIRED_CONTRACT',reason='1338 individual ordinary Web source applicability: '+reason,
            diagnosticFragment=fragment(path.read_text(),row),rawWarningRetained=True,owningPhysicalClassHashes=family,
            plannedCurrentWholeCaseClasses=declarations,currentWholeCaseRefs=[],currentWholeJoinPending=True,
            actualRuntimeProven=False,formalAccepted=False,F03Accepted=False,ptAlternativeCompleted=0,
            reviewScope='APPLICABILITY_ONLY_NOT_RUNTIME_OR_COVERAGE_ACCEPTANCE'))
    if found!=Counter({(name,key):v[0]for name,sites in SPEC.items()for key,v in sites.items()})or len(decisions)!=33:raise ValueError('all33 explicit span multiplicities')
    updated=apply_decisions(rows,decisions)
    return decisions,dict(actualExit=0,source=source,baseManifestPath=PLAN.relative_to(ROOT).as_posix(),baseManifestSha256=PLAN_SHA,
        rawFindings=1350,statusCounts=dict(Counter(r['status']for r in updated)),reviewed=33,pmdRawRemoved=0,testsExecuted=0,
        currentWholeJoinPending=True,newAcceptedLeaves=0,formalAccepted=False,F03Accepted=False,ptAlternativeCompleted=0,effortPercent=None,
        unresolved=['WebHttpServer startup/cleanup generic catches remain unreviewed BUG1561; no blanket primary/Error approval','whole/native/CHR/451/global100/other individual findings pending'])


def main():
    rows,value=calculate();os.umask(0o077);out=BASE/'PG6284-web-owned-static-review-v1';out.mkdir()
    with(out/'decisions.json').open('x')as f:json.dump(rows,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    value['decisionsSha256']=sha(out/'decisions.json')
    with(out/'manifest.json').open('x')as f:json.dump(value,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0,reviewed=33,statusCounts=value['statusCounts'],manifestSha256=sha(out/'manifest.json'))))


if __name__=='__main__':main()
