"""117 individually located current source reviews; no raw removal, PT alternative or runtime claim."""
import json
import os
from collections import Counter
from pathlib import Path
import pg6218_keeper_static_reviews as keeper
import pg6226_consumer_static_reviews as consumer
from pg5940_private_lock_compile import ROOT,W,BASE,sha
from pg6248_normal_phase_qualification import original_source
from static_disposition_overlay import load,apply_decisions,validate_rationales
from pg5958_private_lock_reason_review import fragment

PLAN=BASE/'PG6252-current4034-static-plan-v1/manifest.json'
PLAN_SHA='4047ecb68508c1e2fa5ee3fddad12c99c3e1452ae8e4426903868cfcba479999'
R='REQUIRED_CONTRACT'
N='CONTEXT_NOT_APPLICABLE'
G='AvoidCatchingGenericException'
I='AvoidInstanceofChecksInCatchClause'


def specifications():
    # Exact current coordinates were read with their entire acquisition/callback/close scopes.
    maps={
        'QuestionWorkConsumers':{52:56,57:61,71:77,73:79,76:82,87:97,91:101,92:102,96:106,100:110,101:111,102:112,116:126,120:130,122:132},
        'WebLogConsumers':{63:67,69:73,84:90,87:93,90:96,101:112,105:116,106:117,110:121,114:125,115:126,116:127,135:146,139:150,141:152},
        'SyncRequestConsumers':{71:76,77:82,94:101,97:104,100:107,111:122,115:126,119:130,120:131,124:135,144:155,152:163,153:164,155:166,172:183,173:184,174:185}}
    result={}
    for name,mapping in maps.items():
        result[name]={(mapping[line],rule):value for(line,rule),value in consumer.SPEC[name].items()}
        kind={'QuestionWorkConsumers':79,'WebLogConsumers':93,'SyncRequestConsumers':104}[name]
        result[name][(kind,I)]=(1,R,name+': direct Error permits best-effort rollback only if this context/delivery attempted CAS(false,true) succeeds. Previously attempted unknown rollback is never reissued; typed committed/isolation/unconfirmed paths remain separate. Atomic CAS is not proof of rollback success.')
        retry={'QuestionWorkConsumers':87,'WebLogConsumers':101,'SyncRequestConsumers':113}[name]
        result[name][(retry,G)]=(1,R,name+': JMSException/RTE covers transport, processor and preflight failure. Only same-delivery normal rollback completion allows broker retry. False confirmation publishes halted and fatal notification; Sync terminal CAS notifies at most once. Null/invalid-mode/provider failure is never successful processing or a new local business retry; PG6236 red and PG6246 normal/reset/parallel/error cases are independent evidence.')
    mapping={195:195,225:233,231:241,234:244,244:253,248:258,255:265,256:266}
    result['ServiceProcessResources']={(mapping[line],rule):value for(line,rule),value in keeper.CORE.items()}
    for key,(count,status,reason) in list(result['ServiceProcessResources'].items()):
        if key[0] in (233,241,244):
            reason+=' Current finite helper returns only to its owning native/test entry loop; both entry loops independently have no return/athrow. Returning from this finite action is not release completion.'
            result['ServiceProcessResources'][key]=(count,status,reason)
    result['InboundTransactions']={
        (62,G):(1,R,'Fatal DLQ send/commit can throw checked JMS or unchecked provider failure. Isolation retains the protocol cause by identity, uses the same synchronous phase ports for rollback and throws typed FailedJmsIsolationException; no committed fatal receipt is returned on unknown commit.'),
        (63,'CompareObjectsWithEquals'):(1,R,'Reference inequality prevents Throwable self-suppression when isolation provider throws the same protocol Throwable. User/provider equals does not express exception graph identity.'),
        (86,G):(1,R,'Only actual JMSContext.rollback is protected by this RTE catch. attempted precedes it, confirmed follows normal return outside catch. Original Error is not wrapped; rollback RTE produces typed UnconfirmedJmsRollbackException and never confirms normal completion.'),
        (87,'CompareObjectsWithEquals'):(1,R,'Primary and rollback Throwable references can be identical; distinct-only suppression preserves the original failure graph. equals is not an identity-safe replacement.')}
    result['SyncRequestListener']={(92,G):(1,R,'The transacted listener must roll back transport/processor JMSException or RTE and rethrow the same failure. Four validated boundary inputs/session mode precede this try, so outer callback separately detects unconfirmed preflight. Same-delivery phase ports mark only actual rollback normal return; Error stays fatal.')}
    result['TransactedEventListener']={(92,G):(1,R,'The shared event listener rolls back transport/processor JMSException or RTE before rethrowing the same failure. Its normal commit does not call rollback observers, as both QWK/WLG independent golden routes verify. Null/session mode preflight outside this catch cannot masquerade as confirmed retry.')}
    result['WebManagementServer']={
        (35,'DoNotUseThreads'):(1,N,'Standalone JavaSE loopback management owns this bounded executor, not a Jakarta EE managed thread. Its pre-acquisition field is held by the prepared owner and normal stop requires actual termination, not daemon status.'),
        (46,'AvoidUsingVolatile'):(1,R,'start writes started under stopLock, but promote and ready/HTTP handlers read it without that lock. Volatile is the required publication edge for successful startup; it does not make compound readiness state atomic or prove actual Root completion.'),
        (68,G):(2,R,'After a bound owner starts unsuccessfully, both startup RTE and Error must clean that captured owner. The original failure remains primary except a fatal cleanup Error over nonfatal startup; no success receipt is emitted.'),
        (73,G):(2,R,'Unchecked cleanup can fail independently of startup. Prebuilt fixed IOException diagnostic predates bind, raw provider graph is not attached, original/fatal ranking and identical-Throwable suppression are preserved. Checked cleanup IOException follows the existing separate contract.'),
        (74,I):(4,R,'Both predicates distinguish cleanup Error from nonfatal startup. All four overlapping PMD spans are retained. A fatal secondary can supersede only nonfatal primary; cleanup RTE cannot erase startup Error.'),
        (75,'CompareObjectsWithEquals'):(1,R,'Same Throwable cannot suppress itself. Distinct secondary adds the preallocated fixed marker rather than raw cleanup cause; arbitrary equals would break identity and can execute provider code.'),
        (117,'DoNotUseThreads'):(1,N,'Standalone management creates exactly one private executor with one worker/32 tasks before binding. No managed application-server executor is borrowed; owner retains shutdown/join responsibility.'),
        (124,'DoNotUseThreads'):(1,N,'Private factory names only its own daemon worker web-management. Actual join is still required; this does not create a production permission to manipulate unrelated processes or held Root.'),
        (218,'DoNotUseThreads'):(1,N,'Standalone stop reads current interrupt immediately before vendor stop so the caller notification can be restored. It is not a container-managed thread and not evidence of socket release.'),
        (224,'DoNotUseThreads'):(1,N,'Finally restores the pre-stop current-thread interrupt even if vendor stop clears it or throws. Success caches depend on real started/normal completion, not this flag restoration.'),
        (227,'DoNotUseThreads'):(1,N,'shutdownNow applies only to the prepared owner executor. Request alone is not complete; subsequent actual awaitTermination and started guards remain mandatory.'),
        (229,'DoNotUseThreads'):(1,N,'Finite awaitTermination uses the already validated remaining budget, not an unlimited join or fresh deadline. Timeout remains fixed IOException/UNKNOWN; component tests do not prove actual native termination.'),
        (232,'DoNotUseThreads'):(1,N,'Interrupted join restores the current-thread notification and throws fixed stop-unconfirmed IOException. closed success is not stored, and no outer native resource release is inferred.')}
    return result


def calculate():
    source=original_source();rows=load(PLAN,PLAN_SHA,source)
    qp=BASE/'PG6248-normal-phase-qualification-v1/manifest.json';q=json.loads(qp.read_bytes())
    private=W/'pg6248-normal-phase-qualification-v1/manifest.safe.json'
    if sha(qp)!='4495f3778a40c33c3de9f6fbd1082581fba8f7cf02caafae55687b32928b8bfe'or sha(private)!=q['privateManifestSha256']:
        raise ValueError('actual exact current source/class/static inputs')
    proof=json.loads(private.read_bytes());cp=private.with_name('cases.safe.json')
    if sha(cp)!=q['casesSha256']:raise ValueError('original selected case identities')
    cases=json.loads(cp.read_bytes());spec=specifications();found=Counter();decisions=[]
    for row in rows:
        name=Path(row['sourcePath']).stem;key=(int(row['beginline']),row['rule'])
        if name not in spec or key not in spec[name]:continue
        count,status,reason=spec[name][key];found[(name,key)]+=1
        path=ROOT/row['sourcePath']
        if row['status']!='NOT_REVIEWED_CURRENT_SOURCE'or sha(path)!=row['sourceSha256']or sha(path)!=proof['allSourceHashes'][row['sourcePath']]:
            raise ValueError('exact individual new current-source review, not duplicate or changed source')
        module=row['sourcePath'].split('/')[1].removeprefix('schubert-nk-');owner=module+':'+row['sourcePath'].split('/src/main/java/')[1][:-5]
        family={k:v for k,v in proof['allPhysicalMainSha256'].items()if k==owner+'.class'or k.startswith(owner+'$')}
        if not family:raise ValueError('actual original compiled owner family')
        prefixes=('dev.codex.schubert.nk.api.file.ServiceResourceRetentionTest',)if name=='ServiceProcessResources'else(
            ('dev.codex.schubert.nk.web.bootstrap.WebManagement',)if name=='WebManagementServer'else('dev.codex.schubert.nk.api.messaging.inbound.',))
        refs=[c for c in cases if c['className'].startswith(prefixes)]
        if not refs:raise ValueError('actual relevant original selected refs')
        decisions.append(dict(row,status=status,source=source,reason='1330 individual current PG/source review: '+reason,
            diagnosticFragment=fragment(path.read_text(),row),rawWarningRetained=True,owningPhysicalClassHashes=family,
            originalSelectedCaseRefs=refs,qualificationSha256=sha(qp),currentWholeCaseRefs=[],currentWholeJoinPending=True,
            actualRuntimeProven=False,formalAccepted=False,F03Accepted=False,ptAlternativeCompleted=0,
            reviewScope='APPLICABILITY_ONLY_NOT_GLOBAL_FUNCTIONAL_OR_COVERAGE_ACCEPTANCE'))
    expected=Counter({(name,key):value[0]for name,sites in spec.items()for key,value in sites.items()})
    if found!=expected or len(decisions)!=117:raise ValueError('all117 explicit sites/multiplicities, no generic rule disposition')
    updated=apply_decisions(rows,decisions);validate_rationales(updated)
    value=dict(actualExit=0,source=source,baseManifestPath=PLAN.relative_to(ROOT).as_posix(),baseManifestSha256=PLAN_SHA,
        rawFindings=1343,statusCounts=dict(Counter(r['status']for r in updated)),reviewed=117,newAcceptedLeaves=0,
        pmdRawRemoved=0,testsExecuted=0,currentWholeJoinPending=True,formalAccepted=False,F03Accepted=False,
        ptAlternativeCompleted=0,actualRuntimeProven=False,effortPercent=None,
        unresolved=['remaining individual applicability not classified','current whole/original artifacts/global100/native/CHR/451/trace/formal remain separate'])
    return decisions,value


def main():
    rows,value=calculate();os.umask(0o077);out=BASE/'PG6254-ss319-static-review-v1';out.mkdir()
    with(out/'decisions.json').open('x')as f:json.dump(rows,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    value['decisionsSha256']=sha(out/'decisions.json')
    with(out/'manifest.json').open('x')as f:json.dump(value,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0,reviewed=117,statusCounts=value['statusCounts'],manifestSha256=sha(out/'manifest.json'))))


if __name__=='__main__':main()
