"""Current64 exact static/domain qualification and approved three-status API-store projection."""
import hashlib
import json
import re
import subprocess
import pg7310_api_async_metric_review as review
import pg7372_api_pool_observation_review as previous
import pg7394_api_outbox_rows_six_compile as compilation

DDL='src/schubert-nk-api/src/main/resources/db/migration/V003__business_message_log_and_web_tables.sql'
METRIC='src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/monitoring/OutboxRowsMetricRecorder.java'

def blob(path,source=compilation.SOURCE):
    return subprocess.check_output(['git','show',source+':'+path],cwd=review.host.ROOT)

def projection(ddl,metric):
    sql=re.search(r'CONSTRAINT ck_mq_outbox_status CHECK \(status IN \(([^)]+)\)\)',ddl.decode())
    java=re.search(r'public enum Status\s*\{([^}]+)\}',metric.decode(),re.S)
    review.require(sql is not None and java is not None,'exact canonical DDL/status enum')
    a=re.findall(r"'([A-Z]+)'",sql.group(1));b=re.findall(r'\b[A-Z]+\b',java.group(1))
    review.require(len(a)==len(b)==3 and set(a)==set(b)=={'PENDING','SENT','ERROR'},'closed three existing statuses')
    compact=''.join(metric.decode().split())
    review.require('Gauge.builder("nk_outbox_rows",' in compact
      and re.findall(r'\.tag\(([^)]+)\)',compact)==['"store","API"','"status",status.name('],
      'API fixed store/status labels only, no owner/body/identifiers')
    return dict(statuses=['PENDING','SENT','ERROR'],store='API',metric='nk_outbox_rows',labels=['store','status'])

if __name__=='__main__':
    review.SOURCE=compilation.SOURCE;review.OUT=review.host.BASE/'PG7400-api-outbox-rows-review-v1'
    review.CURRENT_TESTS=64;review.CURRENT_SUITES=8;review.CURRENT_EXECUTABLE=15
    review.PHYSICAL_COUNT=1738;review.ADDED_PHYSICAL=69
    review.PREVIOUS_COUNT=77;review.INTRODUCED_COUNT=2;review.CHANGED_COUNT=0
    previous.compilation=compilation;review.STATIC_CLASSIFIER=previous.classify
    review.PINS=dict(review.PINS)
    for key,path in {
      'currentApi':'PG7392-api-outbox-rows-post-v1/manifest.json',
      'physical':'PG7396-api-outbox-rows-six-post-v1/manifest.json',
      'trace':'PG7398-api-outbox-rows-trace-v1/manifest.json',
      'previous':'PG7384-api-operation-mismatch-trace-v1/manifest.json'}.items():
        review.PINS[key]=(path,review.host.sha(review.host.BASE/path))
    ddl=blob(DDL);metric=blob(METRIC)
    review.require(ddl==blob(DDL,'e7d64fda2453e906ee6ccc5fe718e5c29841e4aa'),'original migration history byte unchanged')
    result=projection(ddl,metric);guards=[]
    for kind in ('unapproved-status','canonical-status-removed','wrong-store','actor-label'):
        a=ddl;b=metric
        if kind=='unapproved-status':b=b.replace(b'    ERROR\n',b'    ERROR, PROCESSING\n')
        elif kind=='canonical-status-removed':a=a.replace(b"status IN ('PENDING', 'SENT', 'ERROR')",b"status IN ('PENDING', 'SENT')",1)
        elif kind=='wrong-store':b=b.replace(b'.tag("store", "API")',b'.tag("store", "WEB")')
        else:b=b.replace(b'.tag("status",',b'.tag("actor",')
        review.require(a!=ddl or b!=metric,'negative mutation actually changed declared input')
        try:projection(a,b)
        except ValueError:guards.append(dict(kind=kind,rejected=True))
        else:raise ValueError('unapproved status/store/label projection accepted')
    path='PG7369-api-pool-harness-review-v1/manifest.json';sha=review.host.sha(review.host.BASE/path)
    review.require(sha=='b7901dc09260aaa9b88109face329921a65236e3e6c7969eccd11bea987cfab4','original harness quality proof')
    harness=json.loads((review.host.BASE/path).read_bytes())
    contract=json.loads((review.host.BASE/review.PINS['contract'][0]).read_bytes())
    inputs={'tools/quality/harnesses/monitoring-api-jobs-pom.xml':harness['afterHarnessSha256'],
      'tools/quality/harnesses/monitoring-pom.xml':contract['harness']['knownBatchSha256'],
      'src/schubert-nk-api/pom.xml':contract['apiPom']['sha256'],DDL:contract['canonicalDdl']['sha256']}
    for name,digest in inputs.items():review.require(hashlib.sha256(blob(name)).hexdigest()==digest,'proper current byte/original contract provenance')
    review.EXTRA_REVIEW=dict(outboxProjection=result,projectionNegativeGuards=guards,
      ddlBytesUnchanged=True,ddlSha256=hashlib.sha256(ddl).hexdigest(),harnessWitness=dict(path=path,sha256=sha),
      contractInputHashes=inputs,newOutboxMetricRawFindings=0,actualDatabaseOrDispatcherActions=0,
      oldestSecondsAccepted=False,webStoreAccepted=False,allPrevious77SourceBytesUnchanged=True)
    review.main()
