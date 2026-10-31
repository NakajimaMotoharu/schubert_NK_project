"""Nineteen maintenance JDBC catch purposes; Source metadata only, no maintenance or DB execution."""
import json
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg16345_jms_generic_twenty_purpose_v2 import byte_span as qualified_byte_span

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
PRIOR=('PG16368-session-revocation-thirteen-purpose-v1','f35179565bf683446935f27af91fce81eca4a900b03bca2b5f9d57a271e55681')
OBS=('PG15930-f03-current-main-review-join-v2','7135192bbeda0d358b91c0d87a5635361398af086a461151466882017f6f3983')
BASE=('PG13253-current-all-java-static-v2','751a5f536623faed78362b14e69da89f5fbdba305acf2b8c1bbbf0811021dbdf')
ADAPTER_POST=('PG16346-jms-generic-twenty-post-v1','9d67e4ee28a6ff2211be179d8382830617d559a2254baae7d204083345da7814')
OUT=data.BASE/'PG16374-maintenance-jdbc-nineteen-purpose-v1'
INBOX="src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/maintenance/InboxCleanup.java"
INSPECTOR="src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/maintenance/InspectorDatabaseConnections.java"
EXPIRY="src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/repository/ExpiryAuditRepository.java"
PINS={
  "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/maintenance/InboxCleanup.java": "014f436f55e803092cb9645697da9b7f09402c32cecb70802ae0a86afd176de0",
  "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/maintenance/InspectorDatabaseConnections.java": "aec17fa943139c5969a89363a7eaa7b78837253ee0262e57e603ef9e1181343d",
  "src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/repository/ExpiryAuditRepository.java": "8d04ab28261de2e41ccc24790d732922f02c823aad5c0f374d6040e99cbe9a7e"
}
KINDS={
  "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/maintenance/InboxCleanup.java": {
    "208": "INBOX_OWNED_PRIMARY",
    "212": "INBOX_ROLLBACK",
    "218": "INBOX_FIXED_CATALOG"
  },
  "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/maintenance/InspectorDatabaseConnections.java": {
    "81": "INSPECTOR_ADMISSION_FAILURE",
    "84": "INSPECTOR_UNRETURNED_CLOSE"
  },
  "src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/repository/ExpiryAuditRepository.java": {
    "292": "EXPIRY_ROW_PRIMARY",
    "299": "EXPIRY_ROW_CLOSE",
    "303": "EXPIRY_STATEMENT_PRIMARY",
    "310": "EXPIRY_STATEMENT_CLOSE",
    "448": "RETAINED_SUCCESS_TWR_PRIMARY",
    "451": "RETAINED_SUCCESS_TWR_SECONDARY"
  }
}
PURPOSES={
  "INBOX_OWNED_PRIMARY": "Owned inspection captures SQL/runtime/Error and rolls back only before committed flag. Late parent-guard failure after commit is not proof mutation rolled back; TWR connection close remains owned.",
  "INBOX_ROLLBACK": "Rollback secondary delegates fatal/non-self attachment and rethrows retained failure; outer connection TWR still closes if classification throws. No protected-row or deletion success is inferred.",
  "INBOX_FIXED_CATALOG": "Outer SQL/runtime uncertainty delegates fatal classification before fixed InboxMaintenanceException without provider text/cause/suppressed retention. Commit/close uncertainty is not an advanced cursor.",
  "INSPECTOR_ADMISSION_FAILURE": "Only acquired nonnull connection failing role/admission setup is closed here before fatal classification/rethrow. Successfully admitted result transfers to caller, not this credential-copy owner.",
  "INSPECTOR_UNRETURNED_CLOSE": "Admission cleanup SQL/runtime/Error attaches to failure before fatal classification. Source properties clear and lock unlock in finally; immutable password String erasure or actual DB close is not proven.",
  "EXPIRY_ROW_PRIMARY": "Read projection/provider SQL/runtime/Error records exact row primary then rethrows; owned rows close in typed finally and outer statement remains protected. Unknown provider failure is not swallowed by pure projection validation.",
  "EXPIRY_ROW_CLOSE": "ResultSet close secondary passes existing JdbcResourceFailures SQL-vs-unknown precedence. Non-SQL primary is kept with new fixed secondary, SQL primary plus unknown cleanup selects cleanup; no actual close success.",
  "EXPIRY_STATEMENT_PRIMARY": "Any read/body/row-close failure is captured as statement primary then propagated; statement cleanup remains in finally, borrowed connection is never committed or closed.",
  "EXPIRY_STATEMENT_CLOSE": "Statement close uses the same explicit SQL-vs-unknown precedence but is a separate ownership scope. Final outer SQL-only catalog must not normalize unknown Runtime/Error.",
  "RETAINED_SUCCESS_TWR_PRIMARY": "Retained SUCCESS helper preserves exact Java-TWR-like semantics: acquired resource primary Throwable triggers release once, then primary rethrow if suppression returns. This is not the read helper precedence table.",
  "RETAINED_SUCCESS_TWR_SECONDARY": "Release Throwable is added directly to primary as required by existing SSC304 TWR contract, including its self-suppression behavior. No substitution with JdbcResourceFailures or graph port, no actual release proof."
}
CONTROLS={
  "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/maintenance/InboxCleanup.java": [
    "verifyTransaction(connection);checkParent();connection.commit();committed=true;",
    "if(!committed)try{connection.rollback();",
    "TemporaryInfrastructureException.attachSecondary(failure,rollbackFailure);",
    "thrownewInboxMaintenanceException();"
  ],
  "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/maintenance/InspectorDatabaseConnections.java": [
    "admit(connection);returnconnection;",
    "connection.close();",
    "TemporaryInfrastructureException.attachSecondary(failure,secondary);",
    "properties.clear();"
  ],
  "src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/repository/ExpiryAuditRepository.java": [
    "rowFailure=failure;throwfailure;",
    "if(JdbcResourceFailures.replace(rowFailure,secondary))throwsecondary;",
    "if(JdbcResourceFailures.replace(statementFailure,secondary))throwsecondary;",
    "primary.addSuppressed(secondary);"
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
    require(len(queue)==69 and prior['combinedSelectedReferences']==1171 and prior['combinedPurposeReviewed']==251,'prior exact scope')
    selected=[v for v in queue if v['path'] in PINS];require(len(selected)==19 and all(v['rule']=='AvoidCatchingGenericException' for v in selected),'exact three Source warnings')
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
        a,b,token=byte_span(texts[path],row['attributes']);require(token in {'RuntimeException','Exception','Error','Throwable'} and texts[path].encode()[a:b]==token.encode(),'exact UTF8 type byte span')
        purposes.append(dict(**row,currentSource=SOURCE,reviewStatus='CURRENT_STATIC_MAINTENANCE_JDBC_CATCH_PURPOSE_REVIEW_COMPLETE_NOT_EXECUTED',purposeKind=kind,manualPurpose=PURPOSES[kind],
            residualRisk='Direct Source/manual policy only; no Graph, actual DB/maintenance/credential/inspection/rollback/close success or native resource assurance. TWR contract differs from typed failure precedence.',
            baselineManifestSha256=BASE[1],baselineDiagnosticRowSha256=data.sha(wire(original)),baselineDiagnostic=original,originalDiagnosticSha256=data.sha(original['message'].encode()),
            canonicalSpanStart=a,canonicalSpanEndExclusive=b,canonicalSpanSha256=data.sha(token.encode()),spanBasis='RAW_PREFIX_BEFORE_LATER_ESCAPE_QUALIFIED_UTF8_HALFOPEN',
            dynamicGraphDependencyUnresolved=True,componentSpecificErrorPriorityRetained=True,productTestsExecuted=0,ptExecutionExempt=False,currentWholeCaseRefs=[]))
    ids={v['id'] for v in purposes};remaining=[v for v in queue if v['id'] not in ids]
    clauses=len({(v['path'],v['attributes']['beginline']) for v in purposes});require(len(remaining)==50 and clauses==11,'19 warning rows/11 clauses, no PT count inflation')
    approved_hashes={}
    for design in ["documents/300_SS/310_アプリケーション/312_処理sequence・method・例外・transaction設計.md","documents/300_SS/330_データ・ファイル/332_SQL・transaction・lock・削除設計.md","documents/300_SS/340_batch・基盤/343_設定file・directory・初期data・migration・切戻し設計.md"]:
        approved=(data.ROOT/design).read_bytes()
        require(approved==subprocess.check_output(['git','show','origin/main:'+design],cwd=data.ROOT),'approved design unchanged')
        approved_hashes[design]=data.sha(approved)
    for v in (prior,obs,base,adapter_post):verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'purposes.json',purposes);data.write(OUT/'remaining-selected-review-queue.json',remaining)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,priorManifestSha256=PRIOR[1],priorQueueSha256=prior['queueSha256'],sourceHashes=PINS,
        baselineManifestSha256=BASE[1],baselineFindingsSha256=base['findingsSha256'],adapterPostSha256=ADAPTER_POST[1],approvedDesignHashes=approved_hashes,
        purposesSha256=data.sha((OUT/'purposes.json').read_bytes()),queueSha256=data.sha((OUT/'remaining-selected-review-queue.json').read_bytes()),newManualReviews=19,newReferenceConnections=0,firstEverSemanticReasons=None,
        combinedSelectedReferences=1171,combinedPurposeReviewed=270,combinedPurposeOrReferenceRows=1441,remainingSelectedUnreferenced=50,sourceCatchClauses=clauses,directContractMetadataNegativeVectors=len(labels),directContractNegativeLabels=labels,
        productTestsExecuted=0,ptExecutionExempt=False,sourceChanged=False,rawSuppressed=0,actualViolationCount=None,wholeF03Accepted=False,whole451Accepted=False,externalActions=0,newAccepted=0,formalUpdated=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
