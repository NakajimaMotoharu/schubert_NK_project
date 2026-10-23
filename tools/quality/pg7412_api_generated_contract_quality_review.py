"""Current72/raw8/source80/projection and explicit generated21 contract review; no PT/coverage union."""
import hashlib
import json
import subprocess
import pg7310_api_async_metric_review as review
import pg7372_api_pool_observation_review as previous
import pg7400_api_outbox_rows_review as outbox
import pg7406_api_generated_contract_six_compile as compilation

def blob(path):
    return subprocess.check_output(['git','show',compilation.SOURCE+':'+path],cwd=review.host.ROOT)

if __name__=='__main__':
    review.SOURCE=compilation.SOURCE;review.OUT=review.host.BASE/'PG7412-api-generated-contract-quality-review-v1'
    review.CURRENT_TESTS=72;review.CURRENT_SUITES=9;review.CURRENT_EXECUTABLE=15
    review.PHYSICAL_COUNT=1738;review.ADDED_PHYSICAL=69
    review.PREVIOUS_COUNT=77;review.INTRODUCED_COUNT=3;review.CHANGED_COUNT=0
    previous.compilation=compilation;review.STATIC_CLASSIFIER=previous.classify
    review.PINS=dict(review.PINS)
    for key,path in {
      'currentApi':'PG7404-api-generated-contract-post-v1/manifest.json',
      'physical':'PG7408-api-generated-contract-six-post-v1/manifest.json',
      'trace':'PG7410-api-generated-contract-trace-v1/manifest.json',
      'previous':'PG7384-api-operation-mismatch-trace-v1/manifest.json'}.items():
        review.PINS[key]=(path,review.host.sha(review.host.BASE/path))
    ddl=blob(outbox.DDL);metric=blob(outbox.METRIC);projection=outbox.projection(ddl,metric);guards=[]
    for kind in ('unapproved-status','canonical-status-removed','wrong-store','actor-label'):
        a=ddl;b=metric
        if kind=='unapproved-status':b=b.replace(b'    ERROR\n',b'    ERROR, PROCESSING\n')
        elif kind=='canonical-status-removed':a=a.replace(b"status IN ('PENDING', 'SENT', 'ERROR')",b"status IN ('PENDING', 'SENT')",1)
        elif kind=='wrong-store':b=b.replace(b'.tag("store", "API")',b'.tag("store", "WEB")')
        else:b=b.replace(b'.tag("status",',b'.tag("actor",')
        review.require(a!=ddl or b!=metric,'negative projection mutation actually changed input')
        try:outbox.projection(a,b)
        except ValueError:guards.append(dict(kind=kind,rejected=True))
        else:raise ValueError('unapproved outbox projection mutation accepted')
    generated_path='PG7413-api-generated-value-review-v2/manifest.json'
    generated_sha=review.host.sha(review.host.BASE/generated_path)
    review.require(generated_sha=='7d108ca7499763b5ed5526e60144276ace055c66aa88e380a0ccde0a3be2a82e','original generated-method review source/pin')
    generated=json.loads((review.host.BASE/generated_path).read_bytes())
    review.require(generated['source']==compilation.SOURCE and generated['actualExit']==0
      and generated['generatedMethodCount']==21 and generated['actualNewOrdinaryCases']==8
      and generated['currentWholeComponentTests']==72 and generated['productionMainAndMetadataBytesUnchanged']
      and not generated['customExclusionsAdded'] and not generated['qualityConditionChanged'],
      'actual generated21 direct contracts, no numerator/policy modification')
    harness_path='PG7369-api-pool-harness-review-v1/manifest.json';harness_sha=review.host.sha(review.host.BASE/harness_path)
    review.require(harness_sha=='b7901dc09260aaa9b88109face329921a65236e3e6c7969eccd11bea987cfab4','original harness quality proof')
    harness=json.loads((review.host.BASE/harness_path).read_bytes())
    contract=json.loads((review.host.BASE/review.PINS['contract'][0]).read_bytes())
    inputs={'tools/quality/harnesses/monitoring-api-jobs-pom.xml':harness['afterHarnessSha256'],
      'tools/quality/harnesses/monitoring-pom.xml':contract['harness']['knownBatchSha256'],
      'src/schubert-nk-api/pom.xml':contract['apiPom']['sha256'],outbox.DDL:contract['canonicalDdl']['sha256']}
    for path,sha in inputs.items():review.require(hashlib.sha256(blob(path)).hexdigest()==sha,'each actual current input to proper original witness')
    prefix='dev/codex/schubert/nk/api/monitoring/'
    mappings={prefix+name:ids for name,ids in {
      'DbPoolMetricRecorder$Counts':['GENMET001','GENMET002'],
      'OutboxRowsMetricRecorder$Counts':['GENMET003','GENMET004'],
      'AsyncJobMetricRecorder$State':['GENMET005'],
      'DbPoolMetricRecorder$State':['GENMET006'],
      'OperationMismatchMetricRecorder$Operation':['GENMET007'],
      'OutboxRowsMetricRecorder$Status':['GENMET008']}.items()}
    review.require(set(mappings)=={row['className'] for row in generated['generatedTypes']},'all six exact generated types have precise test IDs')
    trace=json.loads((review.host.BASE/review.PINS['trace'][0]).read_bytes())
    by_path={row['path']:row for row in trace['sourceRows']}
    for row in generated['generatedTypes']:
        source='src/schubert-nk-api/src/main/java/'+row['className'].split('$',1)[0]+'.java'
        review.require(source in by_path and by_path[source]['additionalTestIdFamily']=='GENMET001..008'
          and len(by_path[source]['additionalSpecifications'])==1,'all generated source parents link explicit1650 oracle')
    review.EXTRA_REVIEW=dict(outboxProjection=projection,projectionNegativeGuards=guards,
      generatedReview=dict(path=generated_path,sha256=generated_sha),generatedTypeTestIds=mappings,
      generatedMethodsVerifiedSeparatelyNotAddedToCounters=21,contractInputHashes=inputs,
      old64OrdinaryResultRetained=True,newGeneratedTestDefinitionNotArithmeticPass=True,
      whole451Accepted=False,relatedBugs=['BUG-1660','BUG-1661'],relatedExpansions=['YKT-1413','YKT-1414'])
    review.main()
