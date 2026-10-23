"""Current56 qualification plus closed eight-purpose projection, no token/HMAC/key/auth operation."""
import hashlib
import json
import re
import subprocess
import pg7310_api_async_metric_review as review
import pg7372_api_pool_observation_review as previous
import pg7380_api_operation_mismatch_six_compile as compilation

WEB='src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/session/SessionOperationToken.java'
METRIC='src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/monitoring/OperationMismatchMetricRecorder.java'
EXPECTED={'UCRREQ01','USTREQ01','URLREQ01','UPWREQ01','ULKREQ01','QSBREQ01','NTCREQ01','QDLREQ01'}

def blob(path,source=compilation.SOURCE):
    return subprocess.check_output(['git','show',source+':'+path],cwd=review.host.ROOT)

def catalog(web,metric):
    purpose=re.search(r'PURPOSES\s*=\s*Set.of\((.*?)\);',web.decode(),re.S)
    operations=re.search(r'public enum Operation\s*\{([^}]+)\}',metric.decode(),re.S)
    review.require(purpose is not None and operations is not None,'literal canonical purpose/operation enums')
    a=re.findall(r'"([A-Z0-9]{8})"',purpose.group(1));b=re.findall(r'\b[A-Z][A-Z0-9]{7}\b',operations.group(1))
    review.require(len(a)==len(b)==8 and set(a)==set(b)==EXPECTED,'exact eight approved update purposes, not login/free-form values')
    compact=''.join(metric.decode().split())
    review.require('publicvoidrecord(Operationoperation)' in compact
      and 'Counter.builder("nk_operation_token_mismatch_total")' in compact
      and re.findall(r'\.tag\(([^)]+)\)',compact)==['"operation",operation.name('],
      'typed operation observation and exact single closed label, no actor/token data')
    return dict(operations=sorted(EXPECTED),counter='nk_operation_token_mismatch_total',labels=['operation'])

if __name__=='__main__':
    review.SOURCE=compilation.SOURCE;review.OUT=review.host.BASE/'PG7386-api-operation-mismatch-review-v1'
    review.CURRENT_TESTS=56;review.CURRENT_SUITES=7;review.CURRENT_EXECUTABLE=12
    review.PHYSICAL_COUNT=1735;review.ADDED_PHYSICAL=66
    review.PREVIOUS_COUNT=75;review.INTRODUCED_COUNT=2;review.CHANGED_COUNT=0
    previous.compilation=compilation;review.STATIC_CLASSIFIER=previous.classify
    review.PINS=dict(review.PINS)
    for key,path in {
      'currentApi':'PG7378-api-operation-mismatch-post-v1/manifest.json',
      'physical':'PG7382-api-operation-mismatch-six-post-v1/manifest.json',
      'trace':'PG7384-api-operation-mismatch-trace-v1/manifest.json',
      'previous':'PG7370-api-pool-observation-trace-v1/manifest.json'}.items():
        review.PINS[key]=(path,review.host.sha(review.host.BASE/path))
    web=blob(WEB);metric=blob(METRIC)
    review.require(web==blob(WEB,'e7d64fda2453e906ee6ccc5fe718e5c29841e4aa'),'original public Web purpose byte unchanged; no business/secret use')
    projection=catalog(web,metric);guards=[]
    for kind in ('unapproved-operation','missing-canonical-purpose','actor-label','wrong-metric-name'):
        a=web;b=metric
        if kind=='unapproved-operation':b=b.replace(b'    QDLREQ01\n',b'    QDLREQ01, LGNREQ01\n')
        elif kind=='missing-canonical-purpose':a=a.replace(b'"QDLREQ01"',b'"QXXREQ01"')
        elif kind=='actor-label':b=b.replace(b'.tag("operation",',b'.tag("actor",')
        else:b=b.replace(b'nk_operation_token_mismatch_total',b'nk_other_total')
        review.require(a!=web or b!=metric,'negative mutation actually changed input')
        try:catalog(a,b)
        except ValueError:guards.append(dict(kind=kind,rejected=True))
        else:raise ValueError('unapproved projection mutation accepted')
    path='PG7369-api-pool-harness-review-v1/manifest.json';digest=review.host.sha(review.host.BASE/path)
    review.require(digest=='b7901dc09260aaa9b88109face329921a65236e3e6c7969eccd11bea987cfab4','original six-guard harness witness')
    harness=json.loads((review.host.BASE/path).read_bytes())
    contract=json.loads((review.host.BASE/review.PINS['contract'][0]).read_bytes())
    inputs={'tools/quality/harnesses/monitoring-api-jobs-pom.xml':harness['afterHarnessSha256'],
      'tools/quality/harnesses/monitoring-pom.xml':contract['harness']['knownBatchSha256'],
      'src/schubert-nk-api/pom.xml':contract['apiPom']['sha256'],contract['canonicalDdl']['path']:contract['canonicalDdl']['sha256']}
    for name,sha in inputs.items():review.require(hashlib.sha256(blob(name)).hexdigest()==sha,'each current byte to its appropriate actual original contract input')
    review.EXTRA_REVIEW=dict(operationCatalog=projection,operationNegativeGuards=guards,
      publicWebPurposeSourceSha256=hashlib.sha256(web).hexdigest(),publicWebPurposeUnchanged=True,
      harnessWitness=dict(path=path,sha256=digest),contractInputHashes=inputs,
      newOperationMetricRawFindings=0,actualTokenHmacKeyAuthOperations=0,allPrevious75SourceBytesUnchanged=True)
    review.main()
