"""Twenty-two question/local audit Source catch purposes; zero-translation qualified, no Product execution."""
import json
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pmd_source_span_no_unicode_translation import span as byte_span

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
PRIOR=('PG16380-batch-phase-eighteen-purpose-v1','db29b0860008a141a128ebe3dd6e97d7870dbd5a8c2cf91542cd57c18566bcae')
OBS=('PG15930-f03-current-main-review-join-v2','7135192bbeda0d358b91c0d87a5635361398af086a461151466882017f6f3983')
BASE=('PG13253-current-all-java-static-v2','751a5f536623faed78362b14e69da89f5fbdba305acf2b8c1bbbf0811021dbdf')
ADAPTER_POST=('PG16346-jms-generic-twenty-post-v1','9d67e4ee28a6ff2211be179d8382830617d559a2254baae7d204083345da7814')
QUAL=('PG16386-zero-unicode-span-qualification-v1','a867f250314fe3d1a670f09e85e15d3e82067a125bcd2e94e90dc1a746d568a0')
QUAL_POST=('PG16388-zero-unicode-span-independent-v1','8cb0a1383eb69550600464a4a2884e2bbc06071640623fc41c3fd3b29860ac1f')
OUT=data.BASE/'PG16392-question-local-audit-twentytwo-purpose-v1'
SUBMISSION="src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/application/question/QuestionSubmissionService.java"
WORKER="src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/application/question/QuestionWorkerService.java"
LOG="src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/logging/WebRequestLogProducer.java"
PINS={
  "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/application/question/QuestionSubmissionService.java": "d303f5a79375d69bbc4f45c91d4ab74bd5744c40baafe45f6cbe8beb692ffaa2",
  "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/application/question/QuestionWorkerService.java": "e3cf7a1056e03ce46380893697cb2d2faefa02a88ea966a14ff99646763b3c83",
  "src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/logging/WebRequestLogProducer.java": "f68eb4c356f08234f64c9ab39af6f463933fe0e69fac7cab35feb24875b80b0e"
}
KINDS={
  "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/application/question/QuestionSubmissionService.java": {
    "138": "SUBMISSION_OUTER_FAILURE",
    "206": "SUBMISSION_ACCEPTANCE_TX",
    "484": "SUBMISSION_SENT_TX",
    "589": "SUBMISSION_RETAINED_AUDIT_TX",
    "756": "SUBMISSION_ROLLBACK"
  },
  "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/application/question/QuestionWorkerService.java": {
    "139": "WORKER_PROVIDER_RUNTIME",
    "153": "WORKER_OUTER_FAILURE",
    "666": "WORKER_TX_FAILURE",
    "669": "WORKER_TX_ROLLBACK"
  },
  "src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/logging/WebRequestLogProducer.java": {
    "202": "PROJECTION_FAILED_AUDIT",
    "231": "LOCAL_LOGGER_RUNTIME",
    "237": "LOCAL_TERMINAL_RUNTIME",
    "282": "PROJECTION_TX_FAILURE",
    "285": "PROJECTION_ROLLBACK_ORDINARY",
    "287": "PROJECTION_ROLLBACK_ERROR"
  }
}
PURPOSES={
  "SUBMISSION_OUTER_FAILURE": "After decoded request TWR close, SQL/runtime uncertainty delegates fatal classification then fixed infrastructure exception. Separate permanent protocol branch retains its suppressed-uncertainty rule; no new request/result is invented.",
  "SUBMISSION_ACCEPTANCE_TX": "Acceptance timeout/execute/commit SQL/runtime/Error failure attempts rollback before rethrow through owned connection TWR. Outcome cannot escape connection close; atomic persistence/SENT success is not inferred.",
  "SUBMISSION_SENT_TX": "Connection-bounded read-only SENT proof commits before returning boolean; SQL/runtime/Error failure rolls back and rethrows through TWR. Outer monotonic budget remains authoritative, not synthetic sent success.",
  "SUBMISSION_RETAINED_AUDIT_TX": "Retained rejection audit has a separate owned short transaction; failure rolls back before TWR close and propagates. It never restores old processing history or creates new acceptance.",
  "SUBMISSION_ROLLBACK": "Rollback secondary delegates common attachment; acquired connection TWR is still active on fatal propagation. No transitive Graph identity/finite-return or actual rollback outcome is proven.",
  "WORKER_PROVIDER_RUNTIME": "Provider runtime delegates fatal check first; below actual count4 it becomes temporary failure, at terminal count it records SYSTEM_UNAVAIL and requires saved DLQ dispatch SENT before normal return. No provider retry or SENT is executed in this review.",
  "WORKER_OUTER_FAILURE": "SQL/runtime work uncertainty becomes fixed temporary failure after fatal delegation; wire buffer finally wipe remains. Durable ERROR proof inconsistency has its separate temporary path, not fatal-ACK success.",
  "WORKER_TX_FAILURE": "Each short database work owns commit and connection TWR; SQL/runtime/Error failure attempts rollback, rethrows and closes before provider/waiting proceeds. No actual job transition is proven.",
  "WORKER_TX_ROLLBACK": "Rollback SQL/runtime/Error delegates attachment while outer TWR retains owned close; no additional rollback, graph execution or success conversion.",
  "PROJECTION_FAILED_AUDIT": "Only ordinary projection SQL/runtime reaches local FAILED supplement after local PENDING; fatal is classified first. HTTP result/event identity stays unchanged; failed projection is not successful audit.",
  "LOCAL_LOGGER_RUNTIME": "Primitive logger runtime is retained until the existing terminal signal is attempted. Direct logger Error bypasses this Runtime catch and is not converted to false or a successful local record.",
  "LOCAL_TERMINAL_RUNTIME": "Callback Runtime graph is classified before retained logger Runtime graph; only returning nonfatal paths throw fixed signal-failed catalog. Direct callback Error keeps existing immediate priority, no repeat notification.",
  "PROJECTION_TX_FAILURE": "Owned REQUEST projection SQL/runtime/Error failure attempts rollback before rethrow through connection TWR. Commit/close uncertainty does not return successful enqueue.",
  "PROJECTION_ROLLBACK_ORDINARY": "Rollback SQL/runtime secondary delegates graph attachment to retained primary, preserving existing direct-Error branch separately. TWR still closes if helper propagates fatal.",
  "PROJECTION_ROLLBACK_ERROR": "Existing component contract gives direct rollback Error priority even over a different primary Error, with non-self primary attachment. Do not normalize this to API first-primary-Error policy."
}
CONTROLS={
  "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/application/question/QuestionSubmissionService.java": [
    "Outcomeoutcome=execute(connection,request,received,start,budget);connection.commit();returnoutcome;",
    "rollback(connection,failure);throwfailure;",
    "if(expired(start,budget))returnfailure(request,ResultCode.TEMPORARY_FAILURE);",
    "TemporaryInfrastructureException.attachSecondary(failure,rollback);"
  ],
  "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/application/question/QuestionWorkerService.java": [
    "TemporaryInfrastructureException.preserveFatal(unavailable);if(delivery.deliveryCount()<TERMINAL_DELIVERY_COUNT)",
    "if(failedinstanceofPendingDlqpending)awaitSent(event.header(),wire,pending);",
    "TemporaryInfrastructureException.attachSecondary(failure,cleanup);",
    "Arrays.fill(wire,(byte)0);"
  ],
  "src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/logging/WebRequestLogProducer.java": [
    "if(!local(localLevel,json))return;",
    "localFailure=failure;",
    "WebStartupException.preserveFatal(failedSignal);if(localFailure!=null)WebStartupException.preserveFatal(localFailure);",
    "if(fatal!=failure)fatal.addSuppressed(failure);throwfatal;"
  ]
}

def require(ok,why):
    if not ok:raise ValueError(why)

def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def wire(v):return json.dumps(v,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()

def controls(path,text):
    compact=''.join(text.split())
    require(all(v in compact for v in CONTROLS[path]),'reviewed explicit Source controls')

def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    prior,obs,base,adapter_post=[read(v) for v in (PRIOR,OBS,BASE,ADAPTER_POST)]
    qualification,qualification_post=[read(v) for v in (QUAL,QUAL_POST)]
    require(qualification['actualExit']==qualification_post['actualExit']==0 and qualification['source']==qualification_post['source']==SOURCE and qualification_post['parentManifestSha256']==QUAL[1],'zero-translation qualification')
    helper_hash='5d0866d2f000218feda73ba52f8079c9834eeb8a101b4cb54bc60b7e76296df2'
    require(qualification['helperSha256']==qualification_post['helperSha256']==helper_hash==data.sha((data.ROOT/qualification['helper']).read_bytes()),'same qualified helper')
    qualified_spans=data.read_checked(data.BASE/QUAL[0]/'spans.json',qualification['spansSha256'])
    require(all(v['actualExit']==0 for v in (prior,obs,base,adapter_post)) and prior['source']==obs['source']==adapter_post['source']==SOURCE
            and adapter_post['utf8ByteNegativeVectors']==4,'qualified static chain and UTF8 adapter')
    queue=data.read_checked(data.BASE/PRIOR[0]/'remaining-selected-review-queue.json',prior['queueSha256'])
    require(len(queue)==32 and prior['combinedSelectedReferences']==1171 and prior['combinedPurposeReviewed']==288,'prior exact scope')
    selected=[v for v in queue if v['path'] in PINS];require(len(selected)==22 and all(v['rule']=='AvoidCatchingGenericException' for v in selected),'exact three Source warnings')
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
        qualified=[v for v in qualified_spans if v['path']==path and v['attributes']==row['attributes']]
        require(len(qualified)==1 and qualified[0]['sourceSha256']==PINS[path] and qualified[0]['canonicalSpanStart']==a and qualified[0]['canonicalSpanEndExclusive']==b and qualified[0]['canonicalSpanSha256']==data.sha(token.encode()),'same original qualified diagnostic span')
        purposes.append(dict(**row,currentSource=SOURCE,reviewStatus='CURRENT_STATIC_QUESTION_LOCAL_AUDIT_CATCH_PURPOSE_REVIEW_COMPLETE_NOT_EXECUTED',purposeKind=kind,manualPurpose=PURPOSES[kind],
            residualRisk='Direct Source/manual policy only; no Graph/provider/callback finite return, actual DB/JMS/session/crypto/SENT/ACK/retry/HTTP/owned close or native assurance.',
            baselineManifestSha256=BASE[1],baselineDiagnosticRowSha256=data.sha(wire(original)),baselineDiagnostic=original,originalDiagnosticSha256=data.sha(original['message'].encode()),
            canonicalSpanStart=a,canonicalSpanEndExclusive=b,canonicalSpanSha256=data.sha(token.encode()),spanBasis='JLS25_ZERO_ELIGIBLE_UNICODE_ESCAPE_UTF8_HALFOPEN',
            dynamicGraphDependencyUnresolved=True,componentSpecificErrorPriorityRetained=True,productTestsExecuted=0,ptExecutionExempt=False,currentWholeCaseRefs=[]))
    ids={v['id'] for v in purposes};remaining=[v for v in queue if v['id'] not in ids]
    clauses=len({(v['path'],v['attributes']['beginline']) for v in purposes});require(len(remaining)==10 and clauses==15,'22 warning rows/15 clauses, no PT count inflation')
    approved_hashes={}
    for design in ["documents/300_SS/310_アプリケーション/312_処理sequence・method・例外・transaction設計.md","documents/300_SS/320_メッセージング/324_Outbox・Inbox・冪等性・再送設計.md","documents/300_SS/350_運用・品質/351_Log・metric・alert・error code設計.md"]:
        approved=(data.ROOT/design).read_bytes()
        require(approved==subprocess.check_output(['git','show','origin/main:'+design],cwd=data.ROOT),'approved design unchanged')
        approved_hashes[design]=data.sha(approved)
    for v in (prior,obs,base,adapter_post,qualification,qualification_post):verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'purposes.json',purposes);data.write(OUT/'remaining-selected-review-queue.json',remaining)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,priorManifestSha256=PRIOR[1],priorQueueSha256=prior['queueSha256'],sourceHashes=PINS,
        baselineManifestSha256=BASE[1],baselineFindingsSha256=base['findingsSha256'],adapterPostSha256=ADAPTER_POST[1],approvedDesignHashes=approved_hashes,spanQualificationSha256=QUAL[1],spanIndependentQualificationSha256=QUAL_POST[1],spanHelperSha256=helper_hash,
        purposesSha256=data.sha((OUT/'purposes.json').read_bytes()),queueSha256=data.sha((OUT/'remaining-selected-review-queue.json').read_bytes()),newManualReviews=22,newReferenceConnections=0,firstEverSemanticReasons=None,
        combinedSelectedReferences=1171,combinedPurposeReviewed=310,combinedPurposeOrReferenceRows=1481,remainingSelectedUnreferenced=10,sourceCatchClauses=clauses,directContractMetadataNegativeVectors=len(labels),directContractNegativeLabels=labels,
        productTestsExecuted=0,ptExecutionExempt=False,sourceChanged=False,rawSuppressed=0,actualViolationCount=None,wholeF03Accepted=False,whole451Accepted=False,externalActions=0,newAccepted=0,formalUpdated=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
