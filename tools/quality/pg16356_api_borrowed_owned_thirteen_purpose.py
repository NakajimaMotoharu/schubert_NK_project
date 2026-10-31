"""Thirteen API catch purposes; Source metadata only, never Graph or JDBC execution."""
import json
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg16345_jms_generic_twenty_purpose_v2 import byte_span as qualified_byte_span

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
PRIOR=('PG16350-jms-delivery-log-fortyseven-purpose-v1','5e9c475828e8139cfc66417a78cdb09f5d9cb119c21f3e2ef59ae94585a44a19')
OBS=('PG15930-f03-current-main-review-join-v2','7135192bbeda0d358b91c0d87a5635361398af086a461151466882017f6f3983')
BASE=('PG13253-current-all-java-static-v2','751a5f536623faed78362b14e69da89f5fbdba305acf2b8c1bbbf0811021dbdf')
ADAPTER_POST=('PG16346-jms-generic-twenty-post-v1','9d67e4ee28a6ff2211be179d8382830617d559a2254baae7d204083345da7814')
OUT=data.BASE/'PG16356-api-borrowed-owned-thirteen-purpose-v1'
COMMAND="src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/application/question/QuestionCommandService.java"
SYNC="src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/dispatch/JdbcSyncRequestProcessor.java"
LOG="src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/logging/WebLogIngestService.java"
QUERY="src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/persistence/QuestionQueryRepository.java"
PINS={
  "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/application/question/QuestionCommandService.java": "9e188be488c14e55b22a0c6dc65eb90e9f5ba4167bd04620290ad665ae6ab306",
  "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/dispatch/JdbcSyncRequestProcessor.java": "65258747a2876004a921a86841b9bea32cd599a9301d7d6fb9e97c0fcec3db49",
  "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/logging/WebLogIngestService.java": "51f50b7f8f9bc38639b9c269345e7c6c388079cc0696c74a5c590d879dac8a87",
  "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/persistence/QuestionQueryRepository.java": "5eece6ce0bfd2e2e7db0f466f4f2806a28ce4182019117d897f5346468f54efd"
}
KINDS={
  "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/application/question/QuestionCommandService.java": {
    "196": "BORROWED_CANCEL",
    "280": "BORROWED_DELETE"
  },
  "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/dispatch/JdbcSyncRequestProcessor.java": {
    "44": "OWNED_SYNC_FAILURE",
    "47": "OWNED_SYNC_ROLLBACK",
    "57": "OWNED_SYNC_REDACT"
  },
  "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/logging/WebLogIngestService.java": {
    "56": "OWNED_LOG_FAILURE",
    "59": "OWNED_LOG_ROLLBACK"
  },
  "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/persistence/QuestionQueryRepository.java": {
    "313": "BORROWED_QUERY_PAGE",
    "347": "BORROWED_QUERY_DETAIL"
  }
}
PURPOSES={
  "BORROWED_CANCEL": "After caller-owned write transaction checks and statement/result close, SQL/runtime failures delegate fatal classification then fixed infrastructure failure. No new commit, rollback, connection close or success cancellation is inferred.",
  "BORROWED_DELETE": "Logical deletion and audit share the borrowed write transaction; statement/result close precedes outer conversion. Fixed infrastructure failure is not successful deletion and this service does not own commit/rollback.",
  "OWNED_SYNC_FAILURE": "Handler or commit SQL/runtime/Error failure attempts rollback once inside owned TWR connection, then rethrows. Outer close occurs before classification or response return; commit uncertainty is not undone by assumption.",
  "OWNED_SYNC_ROLLBACK": "Rollback SQL/runtime/Error secondary delegates non-self/fatal attachment to the retained primary. TWR still owns connection close if the helper throws; transitive graph identity/finite return is not proven here.",
  "OWNED_SYNC_REDACT": "Outer SQL/runtime failure includes uncertain commit/close and delegates fatal classification before fixed infrastructure catalog. Separate permanent protocol branch checks suppressed uncertainty, not fabricated response/ACK.",
  "OWNED_LOG_FAILURE": "Insert or commit SQL/runtime/Error failure attempts one rollback and rethrows through owned connection TWR. New/duplicate boolean returns only after normal commit/close; no JMS ACK is issued here.",
  "OWNED_LOG_ROLLBACK": "Rollback secondary delegates attachment to original failure within TWR; subsequent close remains compiler-owned. Outer SQL-only redaction is distinct from Runtime/Error propagation and is not broadened by this review.",
  "BORROWED_QUERY_PAGE": "Borrowed read-only page projection converts SQL/runtime to fixed temporary failure after statement/result close. Separate QuestionQueryException preserves definite resource/business code only without suppressed uncertainty; graph behavior remains unexecuted.",
  "BORROWED_QUERY_DETAIL": "Borrowed read-only detail projection returns absent only on definite zero rows; SQL/runtime/result-conversion/statement-close failure delegates fatal classification then temporary result, without owning connection completion."
}
CONTROLS={
  "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/application/question/QuestionCommandService.java": [
    "require(!c.getAutoCommit()&&!c.isReadOnly());",
    "TemporaryInfrastructureException.preserveFatal(failure);thrownewTemporaryInfrastructureException();",
    "audit(c,actor,metadata,\"QUESTION_CANCELLED\"",
    "audit(c,actor,metadata,\"QUESTION_DELETE_MARKED\""
  ],
  "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/dispatch/JdbcSyncRequestProcessor.java": [
    "connection.setAutoCommit(false);",
    "connection.commit();returnresponse;",
    "connection.rollback();",
    "TemporaryInfrastructureException.attachSecondary(failure,rollbackFailure);",
    "if(failure.getSuppressed().length!=0)thrownewTemporaryInfrastructureException();"
  ],
  "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/logging/WebLogIngestService.java": [
    "connection.setAutoCommit(false);",
    "connection.commit();returninserted;",
    "connection.rollback();",
    "TemporaryInfrastructureException.attachSecondary(failure,rollbackFailure);",
    "thrownewLogProjectionDatabaseException();"
  ],
  "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/persistence/QuestionQueryRepository.java": [
    "require(!c.getAutoCommit()&&c.isReadOnly());",
    "if(failure.getSuppressed().length==0)throwfailure;",
    "preserveFatal(failure);thrownewQuestionQueryException(ResultCode.TEMPORARY_FAILURE);",
    "Optional<TypedPayloadValues>result=Optional.empty();"
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
    require(len(queue)==125 and prior['combinedSelectedReferences']==1171 and prior['combinedPurposeReviewed']==195,'prior exact scope')
    selected=[v for v in queue if v['path'] in PINS];require(len(selected)==13 and all(v['rule']=='AvoidCatchingGenericException' for v in selected),'exact four Source warnings')
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
        purposes.append(dict(**row,currentSource=SOURCE,reviewStatus='CURRENT_STATIC_API_BORROWED_OWNED_CATCH_PURPOSE_REVIEW_COMPLETE_NOT_EXECUTED',purposeKind=kind,manualPurpose=PURPOSES[kind],
            residualRisk='Direct Source/manual policy only; no Graph, actual SQL, TWR runtime close, rollback/commit outcome, Throwable-cycle or retry/ACK assurance. No real resource action.',
            baselineManifestSha256=BASE[1],baselineDiagnosticRowSha256=data.sha(wire(original)),baselineDiagnostic=original,originalDiagnosticSha256=data.sha(original['message'].encode()),
            canonicalSpanStart=a,canonicalSpanEndExclusive=b,canonicalSpanSha256=data.sha(token.encode()),spanBasis='RAW_PREFIX_BEFORE_LATER_ESCAPE_QUALIFIED_UTF8_HALFOPEN',
            dynamicGraphDependencyUnresolved=True,componentSpecificErrorPriorityRetained=True,productTestsExecuted=0,ptExecutionExempt=False,currentWholeCaseRefs=[]))
    ids={v['id'] for v in purposes};remaining=[v for v in queue if v['id'] not in ids]
    clauses=len({(v['path'],v['attributes']['beginline']) for v in purposes});require(len(remaining)==112 and clauses==9,'13 warning rows/9 clauses, no PT count inflation')
    design='documents/300_SS/340_batch・基盤/343_設定file・directory・初期data・migration・切戻し設計.md';approved=(data.ROOT/design).read_bytes()
    require(approved==subprocess.check_output(['git','show','origin/main:'+design],cwd=data.ROOT),'approved design unchanged')
    for v in (prior,obs,base,adapter_post):verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'purposes.json',purposes);data.write(OUT/'remaining-selected-review-queue.json',remaining)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,priorManifestSha256=PRIOR[1],priorQueueSha256=prior['queueSha256'],sourceHashes=PINS,
        baselineManifestSha256=BASE[1],baselineFindingsSha256=base['findingsSha256'],adapterPostSha256=ADAPTER_POST[1],approvedDesignSha256=data.sha(approved),
        purposesSha256=data.sha((OUT/'purposes.json').read_bytes()),queueSha256=data.sha((OUT/'remaining-selected-review-queue.json').read_bytes()),newManualReviews=13,newReferenceConnections=0,firstEverSemanticReasons=None,
        combinedSelectedReferences=1171,combinedPurposeReviewed=208,combinedPurposeOrReferenceRows=1379,remainingSelectedUnreferenced=112,sourceCatchClauses=clauses,directContractMetadataNegativeVectors=len(labels),directContractNegativeLabels=labels,
        productTestsExecuted=0,ptExecutionExempt=False,sourceChanged=False,rawSuppressed=0,actualViolationCount=None,wholeF03Accepted=False,whole451Accepted=False,externalActions=0,newAccepted=0,formalUpdated=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
