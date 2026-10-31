"""Thirty management/observation catch purposes; Source metadata, no service or Graph execution."""
import json
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from pg16345_jms_generic_twenty_purpose_v2 import byte_span as qualified_byte_span

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
PRIOR=('PG16356-api-borrowed-owned-thirteen-purpose-v1','e02c92bbc82d40711832235ad83f4d7377bbdfd1c27f31b549d863cf51ff9165')
OBS=('PG15930-f03-current-main-review-join-v2','7135192bbeda0d358b91c0d87a5635361398af086a461151466882017f6f3983')
BASE=('PG13253-current-all-java-static-v2','751a5f536623faed78362b14e69da89f5fbdba305acf2b8c1bbbf0811021dbdf')
ADAPTER_POST=('PG16346-jms-generic-twenty-post-v1','9d67e4ee28a6ff2211be179d8382830617d559a2254baae7d204083345da7814')
OUT=data.BASE/'PG16362-management-observation-thirty-purpose-v1'
API="src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/bootstrap/ApiManagementServer.java"
CONTEXT="src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/monitoring/ApiObservationContext.java"
PUMP="src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/monitoring/ApiOutboxObservationPump.java"
WORKER="src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/monitoring/OwnedApiObservationWorker.java"
HTTP="src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/bootstrap/WebHttpServer.java"
WEB="src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/bootstrap/WebManagementServer.java"
METRIC="src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/monitoring/HttpMetricValve.java"
PINS={
  "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/bootstrap/ApiManagementServer.java": "81c29219808b8c38764d7bcd9ec1d1e7fc32a709a158a0399237e7fe5d46cb5c",
  "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/monitoring/ApiObservationContext.java": "dc1f0876ed10d03d1f60e23567ab6a541be0d61fd253006f83b6b17c55a132f0",
  "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/monitoring/ApiOutboxObservationPump.java": "25eed3a03c68fd2f0bb7c68bf576239e238a2e2ecd4b4003ddc3d076348c2f41",
  "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/monitoring/OwnedApiObservationWorker.java": "8bd8e156ff5038f7e5783865523913e2a0cf6188d674de05c9892ccecc6b0bbf",
  "src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/bootstrap/WebHttpServer.java": "b1e458ef9a9a246f8bb70866dbf671a005bbb569b9c4e27c20b525c20b3180a5",
  "src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/bootstrap/WebManagementServer.java": "f4b820069ae18d539f6ceb62fd2b2e3b95afe27dafb0bdaf72e35c1fe53a01cf",
  "src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/monitoring/HttpMetricValve.java": "f7dd88544d4d690d19a519488904e058a4ee8c2d8b7595c75b0494b872204a75"
}
KINDS={
  "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/bootstrap/ApiManagementServer.java": {
    "70": "API_START_FAILURE",
    "73": "API_START_STOP_FAILURE"
  },
  "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/monitoring/ApiObservationContext.java": {
    "123": "CONTEXT_UNCONFIRMED",
    "127": "CONTEXT_DIAGNOSTIC"
  },
  "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/monitoring/ApiOutboxObservationPump.java": {
    "70": "SAMPLE_CLOCK_FAILURE"
  },
  "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/monitoring/OwnedApiObservationWorker.java": {
    "95": "INTERRUPT_DIAGNOSTIC",
    "101": "WORKER_PRIMARY",
    "104": "WORKER_DIAGNOSTIC",
    "150": "WORKER_STOP_UNCONFIRMED"
  },
  "src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/bootstrap/WebHttpServer.java": {
    "175": "HTTP_START_FAILURE",
    "180": "HTTP_START_DESTROY_FAILURE"
  },
  "src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/bootstrap/WebManagementServer.java": {
    "73": "WEB_START_FAILURE",
    "76": "WEB_START_STOP_FAILURE"
  },
  "src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/monitoring/HttpMetricValve.java": {
    "79": "METRIC_RECORD_FAILURE",
    "89": "METRIC_TERMINAL_FAILURE"
  }
}
PURPOSES={
  "API_START_FAILURE": "Failed component start attempts the retained management stop within its existing 30s contract before rethrow; optional unconfirmed result adds fixed diagnostic, never marks startup success.",
  "API_START_STOP_FAILURE": "Direct cleanup Error outranks non-Error start failure only; an existing start Error is retained, non-self uncertainty adds fixed diagnostic rather than provider graph. Actual server stop/join is unproven.",
  "CONTEXT_UNCONFIRMED": "Close requests worker stop, refuses reentrant/contended owner, awaits worker under original remainder before SDK close. Any IO/runtime/Error latches unconfirmed and notifies policy before fatal classification/rethrow; downstream pool release is not proven.",
  "CONTEXT_DIAGNOSTIC": "Policy callback runtime/Error is attached to primary before declared fatal classification; observer nonreturn and transitive graph semantics are unproven, not normal cleanup.",
  "SAMPLE_CLOCK_FAILURE": "Monotonic clock runtime/Error invalidates observation then rethrows before active claim. Missing is not zero/healthy sample and no implicit next attempt executes here.",
  "INTERRUPT_DIAGNOSTIC": "Unexpected interruption restores flag and notifies owner once; callback failure attaches to interruption, delegates fatal preservation and rethrows diagnostic when helper returns. Stopping interruption differs.",
  "WORKER_PRIMARY": "Unexpected runtime/Error notifies owner then delegates fatal classification and rethrows; finally requests stop. A worker failure is never inferred as sample success or confirmed joined thread.",
  "WORKER_DIAGNOSTIC": "Runtime/Error in failure notification attaches to original worker failure; subsequent classifier may propagate selected fatal. Source policy does not prove callback/graph return.",
  "WORKER_STOP_UNCONFIRMED": "IO/runtime/Error during await permanently latches unconfirmedStop and rethrows. Freeze first remaining plus elapsed budget, actual alive/starting and pump quiescence checks cannot be replaced by requested stop.",
  "HTTP_START_FAILURE": "Native owner callback is before vendor mutation/start; when owner exists catch retains exact phase for native policy without local destroy. Without owner only one local destroy is attempted before rethrow.",
  "HTTP_START_DESTROY_FAILURE": "Ownerless component cleanup attaches distinct destroy failure to the start primary; no graph helper or cleanup success is fabricated. Suppression-disabled primary and actual vendor disposal remain unproven.",
  "WEB_START_FAILURE": "Component start failure attempts retained stop with existing30s and appends returned checked unconfirmed diagnostic before rethrow. This differs from native capture and is not ready/released.",
  "WEB_START_STOP_FAILURE": "Direct stop Error outranks non-Error start primary, otherwise fixed cleanup diagnostic is suppressed when distinct. Web checked-IO/entry-IRQ table is preserved rather than API normalization.",
  "METRIC_RECORD_FAILURE": "Recorder runtime/Error tries owner terminal notification then rethrows retained failure; partial metric recording is not retried or turned into successful observation.",
  "METRIC_TERMINAL_FAILURE": "Failure callback runtime/Error attaches to original observation failure and delegates fatal preservation; only returning nonfatal helper path yields false/fixed metadata diagnostic. Original graphs are not formatted."
}
CONTROLS={
  "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/bootstrap/ApiManagementServer.java": [
    "result.start();returnresult;",
    "closing=result.stopFailure(CLOSE_TIMEOUT);",
    "if(unconfirmedinstanceofError&&!(failureinstanceofError))throwunconfirmed;",
    "if(unconfirmed!=failure)failure.addSuppressed(cleanupDiagnostic);"
  ],
  "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/monitoring/ApiObservationContext.java": [
    "if(worker.isPresent())worker.orElseThrow().awaitStopped(remainingNanos);",
    "metricContext.close();",
    "unconfirmed.set(true);",
    "TemporaryInfrastructureException.attachSecondary(primary,diagnostic);"
  ],
  "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/monitoring/ApiOutboxObservationPump.java": [
    "source.missing();throwfailure;",
    "retained.set(Optional.of(attempt));",
    "if(!stopping.get())source.observe(attempt);",
    "active.set(false);"
  ],
  "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/monitoring/OwnedApiObservationWorker.java": [
    "onFailure.accept(primary);",
    "TemporaryInfrastructureException.attachSecondary(primary,diagnostic);",
    "unconfirmedStop.set(true);throwprimary;",
    "if(!pump.isQuiescent())thrownewIOException(UNCONFIRMED);"
  ],
  "src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/bootstrap/WebHttpServer.java": [
    "if(owner!=null)owner.accept(result);",
    "if(owner==null){try{tomcat.destroy();",
    "if(failure!=cleanup)failure.addSuppressed(cleanup);",
    "throwfailure;"
  ],
  "src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/bootstrap/WebManagementServer.java": [
    "result.start();returnresult;",
    "closing=result.stopFailure(java.time.Duration.ofSeconds(30));",
    "if(unconfirmedinstanceofError&&!(failureinstanceofError))throwunconfirmed;",
    "closing.ifPresent(failure::addSuppressed);"
  ],
  "src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/monitoring/HttpMetricValve.java": [
    "if(!completion.claim())return;",
    "recorder.record(route,method,status,elapsedNanos);",
    "WebStartupException.attachSecondary(failure,signalFailure);",
    "WebStartupException.preserveFatal(failure);returntrue;"
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
    require(len(queue)==112 and prior['combinedSelectedReferences']==1171 and prior['combinedPurposeReviewed']==208,'prior exact scope')
    selected=[v for v in queue if v['path'] in PINS];require(len(selected)==30 and all(v['rule']=='AvoidCatchingGenericException' for v in selected),'exact seven Source warnings')
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
        purposes.append(dict(**row,currentSource=SOURCE,reviewStatus='CURRENT_STATIC_MANAGEMENT_OBSERVATION_CATCH_PURPOSE_REVIEW_COMPLETE_NOT_EXECUTED',purposeKind=kind,manualPurpose=PURPOSES[kind],
            residualRisk='Direct Source policy only; no Graph/callback return, actual bind/start/stop/thread termination, vendor disposal, real DB/SDK closure, UNKNOWN retention/deadline or native assurance.',
            baselineManifestSha256=BASE[1],baselineDiagnosticRowSha256=data.sha(wire(original)),baselineDiagnostic=original,originalDiagnosticSha256=data.sha(original['message'].encode()),
            canonicalSpanStart=a,canonicalSpanEndExclusive=b,canonicalSpanSha256=data.sha(token.encode()),spanBasis='RAW_PREFIX_BEFORE_LATER_ESCAPE_QUALIFIED_UTF8_HALFOPEN',
            dynamicGraphDependencyUnresolved=True,componentSpecificErrorPriorityRetained=True,productTestsExecuted=0,ptExecutionExempt=False,currentWholeCaseRefs=[]))
    ids={v['id'] for v in purposes};remaining=[v for v in queue if v['id'] not in ids]
    clauses=len({(v['path'],v['attributes']['beginline']) for v in purposes});require(len(remaining)==82 and clauses==15,'30 warning rows/15 clauses, no PT count inflation')
    approved_hashes={}
    for design in ["documents/300_SS/310_アプリケーション/312_処理sequence・method・例外・transaction設計.md","documents/300_SS/340_batch・基盤/342_Caddy・systemd・PostgreSQL・Java設定設計.md","documents/300_SS/350_運用・品質/351_Log・metric・alert・error code設計.md"]:
        approved=(data.ROOT/design).read_bytes()
        require(approved==subprocess.check_output(['git','show','origin/main:'+design],cwd=data.ROOT),'approved design unchanged')
        approved_hashes[design]=data.sha(approved)
    for v in (prior,obs,base,adapter_post):verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'purposes.json',purposes);data.write(OUT/'remaining-selected-review-queue.json',remaining)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,priorManifestSha256=PRIOR[1],priorQueueSha256=prior['queueSha256'],sourceHashes=PINS,
        baselineManifestSha256=BASE[1],baselineFindingsSha256=base['findingsSha256'],adapterPostSha256=ADAPTER_POST[1],approvedDesignHashes=approved_hashes,
        purposesSha256=data.sha((OUT/'purposes.json').read_bytes()),queueSha256=data.sha((OUT/'remaining-selected-review-queue.json').read_bytes()),newManualReviews=30,newReferenceConnections=0,firstEverSemanticReasons=None,
        combinedSelectedReferences=1171,combinedPurposeReviewed=238,combinedPurposeOrReferenceRows=1409,remainingSelectedUnreferenced=82,sourceCatchClauses=clauses,directContractMetadataNegativeVectors=len(labels),directContractNegativeLabels=labels,
        productTestsExecuted=0,ptExecutionExempt=False,sourceChanged=False,rawSuppressed=0,actualViolationCount=None,wholeF03Accepted=False,whole451Accepted=False,externalActions=0,newAccepted=0,formalUpdated=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
