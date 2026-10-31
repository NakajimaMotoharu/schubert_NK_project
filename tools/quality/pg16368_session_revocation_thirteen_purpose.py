"""Thirteen session/revocation catch purposes; Source metadata only, not session or DB execution."""
import json
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg16345_jms_generic_twenty_purpose_v2 import byte_span as qualified_byte_span

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
PRIOR=('PG16362-management-observation-thirty-purpose-v1','69b8447ce9d309acb9f9561368648be005fafa58209e8370d2cafdbd70832ce0')
OBS=('PG15930-f03-current-main-review-join-v2','7135192bbeda0d358b91c0d87a5635361398af086a461151466882017f6f3983')
BASE=('PG13253-current-all-java-static-v2','751a5f536623faed78362b14e69da89f5fbdba305acf2b8c1bbbf0811021dbdf')
ADAPTER_POST=('PG16346-jms-generic-twenty-post-v1','9d67e4ee28a6ff2211be179d8382830617d559a2254baae7d204083345da7814')
OUT=data.BASE/'PG16368-session-revocation-thirteen-purpose-v1'
COORD="src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/revocation/RevocationRetryCoordinator.java"
WORKER="src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/revocation/RevocationRetryWorker.java"
SESSION="src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/session/EncryptedWebSessionRepository.java"
PINS={
  "src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/revocation/RevocationRetryCoordinator.java": "974e90ecfa4daafb035c801940593ef63f48d0caf49f11fc355265ca1afe04b2",
  "src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/revocation/RevocationRetryWorker.java": "3db3ddaf2ce6f36c1f783c8ac7bee96dbd71fe8fe5755d58af7637c6010f29e3",
  "src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/session/EncryptedWebSessionRepository.java": "019d4aaab2e5a678959159725fe82217e8cd2d1dce3875ae4e60e7d488fcba92"
}
KINDS={
  "src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/revocation/RevocationRetryCoordinator.java": {
    "122": "REVOCATION_PRIMARY",
    "129": "REVOCATION_ROLLBACK",
    "133": "REVOCATION_DEFER_FATAL",
    "140": "REVOCATION_CLOSE"
  },
  "src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/revocation/RevocationRetryWorker.java": {
    "62": "REVOCATION_CYCLE_FAILURE"
  },
  "src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/session/EncryptedWebSessionRepository.java": {
    "306": "SESSION_PRIMARY",
    "309": "SESSION_ROLLBACK",
    "316": "SESSION_CATALOG"
  }
}
PURPOSES={
  "REVOCATION_PRIMARY": "Captures acquire/setup/work/commit SQL/runtime/Error primary without returning result; rollback is attempted only with an acquired connection and retained failure.",
  "REVOCATION_ROLLBACK": "Rollback SQL/runtime/Error delegates combine/attachment to primary. The enclosing Error catch retains fatal until finally closes the remaining owned connection; transitive helper behavior is not executed.",
  "REVOCATION_DEFER_FATAL": "An Error selected during rollback combination is held as failure instead of escaping before finally-owned connection close. It is not commit success or successful revoke.",
  "REVOCATION_CLOSE": "Acquired connection closes once even if rollback classification selected fatal. Close failure combines with retained primary before final classification; result returns only after normal completion.",
  "REVOCATION_CYCLE_FAILURE": "Unchecked dispatch failure delegates local fatal classification before failed-cycle count. Ordinary failure remains failed; direct Error escapes to uncaught terminal policy, and health flag is not joined-thread proof.",
  "SESSION_PRIMARY": "Setup/work/security/SQL/runtime/Error failure attempts rollback before declared fatal classification and fixed SessionStoreException. Outer TWR remains owner of connection close if classification propagates fatal early.",
  "SESSION_ROLLBACK": "SQL/runtime/Error rollback secondary delegates common attachment; outer TWR still closes acquired connection on early fatal. No actual session/key/crypto/SQL result is inferred.",
  "SESSION_CATALOG": "Outer SQL/runtime includes acquire/commit/close uncertainty; local SessionStore fatal classifier precedes fixed catalog. Missing/invalid outcomes are not session success; close success is unproven."
}
CONTROLS={
  "src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/revocation/RevocationRetryCoordinator.java": [
    "result=Objects.requireNonNull(work.run(connection),\"revocationtransactionresult\");connection.commit();",
    "failure=combine(failure,secondary);",
    "failure=fatal;}finally{if(connection!=null){try{connection.close();",
    "if(failure!=null){preserveFatal(failure);thrownewRevocationRetryException();}"
  ],
  "src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/revocation/RevocationRetryWorker.java": [
    "action.dispatch();completed.incrementAndGet();",
    "RevocationRetryCoordinator.preserveFatal(fixedFailure);failed.incrementAndGet();",
    "if(!thread.join(remaining))",
    "returnactive.get()&&!terminal.get();"
  ],
  "src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/session/EncryptedWebSessionRepository.java": [
    "connection.commit();returnresult;",
    "connection.rollback();",
    "WebStartupException.attachSecondary(failure,rollback);",
    "SessionStoreException.preserveFatal(failure);thrownewSessionStoreException();"
  ]
}

def require(ok,why):
    if not ok:raise ValueError(why)

def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def wire(v):return json.dumps(v,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()

def controls(path,text):
    compact=''.join(text.split())
    require(all(v in compact for v in CONTROLS[path]),'reviewed explicit Source controls')

def byte_span(text,attrs):
    end=attrs.get('endline')
    require(isinstance(end,str) and end.isascii() and end.isdecimal() and int(end)>0,'bounded positive endline')
    lines=text.splitlines(keepends=True);require(int(end)<=len(lines),'bounded actual prefix')
    return qualified_byte_span(''.join(lines[:int(end)]),attrs)

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    prior,obs,base,adapter_post=[read(v) for v in (PRIOR,OBS,BASE,ADAPTER_POST)]
    require(all(v['actualExit']==0 for v in (prior,obs,base,adapter_post)) and prior['source']==obs['source']==adapter_post['source']==SOURCE
            and adapter_post['utf8ByteNegativeVectors']==4,'qualified static chain and UTF8 adapter')
    queue=data.read_checked(data.BASE/PRIOR[0]/'remaining-selected-review-queue.json',prior['queueSha256'])
    require(len(queue)==82 and prior['combinedSelectedReferences']==1171 and prior['combinedPurposeReviewed']==238,'prior exact scope')
    selected=[v for v in queue if v['path'] in PINS];require(len(selected)==13 and all(v['rule']=='AvoidCatchingGenericException' for v in selected),'exact three Source warnings')
    observed={v['staticObservationId']:v for v in data.read_checked(data.BASE/OBS[0]/'current-main-observations.json',obs['observationsSha256'])}
    baseline=data.read_checked(data.BASE/BASE[0]/'findings.json',base['findingsSha256']);texts={p:(data.ROOT/p).read_text() for p in PINS};labels=[]
    for path,text in texts.items():
        require(data.sha(text.encode())==PINS[path],'whole Source unchanged');controls(path,text);compact=''.join(text.split())
        for number,marker in enumerate([CONTROLS[path][0],CONTROLS[path][1],CONTROLS[path][-1]]):
            require(marker in compact,'nondegenerate Source metadata variant');bad=compact.replace(marker,'REMOVED_SOURCE_CONTROL')
            try:controls(path,bad)
            except ValueError:labels.append(path+':'+str(number))
            else:raise ValueError('false source control variant')
    purposes=[]
    for row in selected:
        path=row['path'];o=observed[row['id']];matches=[v for v in baseline if v['path']==path and v['attributes']==row['attributes'] and v['sourceSha256']==row['sourceSha256']]
        require(len(matches)==1,'one original exact diagnostic');original=matches[0];kind=KINDS[path][row['attributes']['beginline']]
        require(o['currentSource']==SOURCE and o['measurementDomain']=='UNCHANGED_MAIN_INPUT_PG13253' and o['sourceSha256']==row['sourceSha256']==PINS[path]
                and o['attributes']==original['attributes'] and o['message']==original['message'],'current Source/attrs/diagnostic origin')
        a,b,token=byte_span(texts[path],row['attributes']);require(token in {'RuntimeException','Exception','Error'} and texts[path].encode()[a:b]==token.encode(),'exact UTF8 type byte span')
        purposes.append(dict(**row,currentSource=SOURCE,reviewStatus='CURRENT_STATIC_SESSION_REVOCATION_CATCH_PURPOSE_REVIEW_COMPLETE_NOT_EXECUTED',purposeKind=kind,manualPurpose=PURPOSES[kind],
            residualRisk='Direct Source/manual policy only; no Graph/Throwable cycle, actual session/key/crypto/SQL/commit-rollback-close, wire retry/ACK or worker termination assurance.',
            baselineManifestSha256=BASE[1],baselineDiagnosticRowSha256=data.sha(wire(original)),baselineDiagnostic=original,originalDiagnosticSha256=data.sha(original['message'].encode()),
            canonicalSpanStart=a,canonicalSpanEndExclusive=b,canonicalSpanSha256=data.sha(token.encode()),spanBasis='RAW_PREFIX_BEFORE_LATER_ESCAPE_QUALIFIED_UTF8_HALFOPEN',
            dynamicGraphDependencyUnresolved=True,componentSpecificErrorPriorityRetained=True,productTestsExecuted=0,ptExecutionExempt=False,currentWholeCaseRefs=[]))
    ids={v['id'] for v in purposes};remaining=[v for v in queue if v['id'] not in ids]
    clauses=len({(v['path'],v['attributes']['beginline']) for v in purposes});require(len(remaining)==69 and clauses==8,'13 warning rows/8 clauses, no PT count inflation')
    approved_hashes={}
    for design in ["documents/300_SS/310_アプリケーション/312_処理sequence・method・例外・transaction設計.md","documents/300_SS/310_アプリケーション/314_認証・認可・session・CSRF実装設計.md","documents/300_SS/330_データ・ファイル/332_SQL・transaction・lock・削除設計.md"]:
        approved=(data.ROOT/design).read_bytes()
        require(approved==subprocess.check_output(['git','show','origin/main:'+design],cwd=data.ROOT),'approved design unchanged')
        approved_hashes[design]=data.sha(approved)
    for v in (prior,obs,base,adapter_post):verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'purposes.json',purposes);data.write(OUT/'remaining-selected-review-queue.json',remaining)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,priorManifestSha256=PRIOR[1],priorQueueSha256=prior['queueSha256'],sourceHashes=PINS,
        baselineManifestSha256=BASE[1],baselineFindingsSha256=base['findingsSha256'],adapterPostSha256=ADAPTER_POST[1],approvedDesignHashes=approved_hashes,
        purposesSha256=data.sha((OUT/'purposes.json').read_bytes()),queueSha256=data.sha((OUT/'remaining-selected-review-queue.json').read_bytes()),newManualReviews=13,newReferenceConnections=0,firstEverSemanticReasons=None,
        combinedSelectedReferences=1171,combinedPurposeReviewed=251,combinedPurposeOrReferenceRows=1422,remainingSelectedUnreferenced=69,sourceCatchClauses=clauses,directContractMetadataNegativeVectors=len(labels),directContractNegativeLabels=labels,
        productTestsExecuted=0,ptExecutionExempt=False,sourceChanged=False,rawSuppressed=0,actualViolationCount=None,wholeF03Accepted=False,whole451Accepted=False,externalActions=0,newAccepted=0,formalUpdated=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
