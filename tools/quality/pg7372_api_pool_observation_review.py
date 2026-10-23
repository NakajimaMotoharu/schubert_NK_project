"""Current48 exact eight raw dispositions/typed getter boundary and new harness provenance."""
import copy
import hashlib
import json
import re
import subprocess
import pg7310_api_async_metric_review as review
import pg7338_api_async_collector_review as previous
import pg7366_api_pool_observation_six_compile as compilation

def blob(path):
    return subprocess.check_output(['git','show',compilation.SOURCE+':'+path],cwd=review.host.ROOT)

def classify(current):
    raw=current['staticRaw']['pmd']
    review.require(raw['actualExit']==4 and raw['processingErrors']==0 and len(raw['findings'])==8,'all eight current raw rows')
    carried=copy.deepcopy(current)
    carried['staticRaw']['pmd']['findings']=[r for r in raw['findings'] if r['class']!='DbPoolMetricCollector']
    previous.compilation=compilation
    result=previous.classify(carried)
    path='src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/monitoring/DbPoolMetricCollector.java'
    code=blob(path);review.require(hashlib.sha256(code).hexdigest()==current['sourceFiles'][path],'actual executed collector bytes')
    compact=''.join(code.decode().split())
    review.require('privatefinalObjectlock=newObject();' in compact and 'synchronized(lock){' in compact
      and 'catch(RuntimeException|ErrorunavailableObservation){metrics.missing();throwunavailableObservation;}' in compact,
      'private owner lock/unknown and same-failure rethrow, not swallowing')
    expected={('AvoidSynchronizedStatement','27','5'),('AvoidCatchingGenericException','34','16'),('AvoidCatchingGenericException','34','35')}
    seen=set()
    for row in raw['findings']:
        if row['class']!='DbPoolMetricCollector':continue
        key=(row.get('rule'),row.get('beginline'),row.get('begincolumn'))
        review.require(key in expected and key not in seen and row.get('method')=='collect'
          and row.get('package')=='dev.codex.schubert.nk.api.monitoring','three exact new context rows only')
        seen.add(key)
        result.append(dict(raw=row,classification='CONTEXT_NOT_APPLICABLE',sourcePath=path,
          sourceSha256=current['sourceFiles'][path],reason='411 private one-owner getter/publication lock and exceptional unknown marking then unchanged Runtime/Error rethrow; POOLCONN003/006/007 verifies failure identity/ordering',
          ordinaryTestWitness='PG7362-api-pool-observation-host-v1',suppressionAdded=False,sourceOrRulesChanged=False))
    review.require(seen==expected,'no additional unclassified or generic rule suppression')
    return result

if __name__=='__main__':
    review.SOURCE=compilation.SOURCE;review.OUT=review.host.BASE/'PG7372-api-pool-observation-review-v1'
    review.CURRENT_TESTS=48;review.CURRENT_SUITES=6;review.CURRENT_EXECUTABLE=10
    review.PHYSICAL_COUNT=1733;review.ADDED_PHYSICAL=64
    review.PREVIOUS_COUNT=71;review.INTRODUCED_COUNT=4;review.CHANGED_COUNT=0;review.STATIC_CLASSIFIER=classify
    review.PINS=dict(review.PINS)
    for key,path in {
      'currentApi':'PG7364-api-pool-observation-post-v1/manifest.json',
      'physical':'PG7368-api-pool-observation-six-post-v1/manifest.json',
      'trace':'PG7370-api-pool-observation-trace-v1/manifest.json',
      'previous':'PG7356-api-pool-metric-trace-v1/manifest.json'}.items():
        review.PINS[key]=(path,review.host.sha(review.host.BASE/path))
    harness_path='PG7369-api-pool-harness-review-v1/manifest.json'
    harness_sha=review.host.sha(review.host.BASE/harness_path)
    review.require(harness_sha=='b7901dc09260aaa9b88109face329921a65236e3e6c7969eccd11bea987cfab4','original independent current harness proof')
    harness=json.loads((review.host.BASE/harness_path).read_bytes())
    review.require(harness['source']==compilation.SOURCE and harness['actualExit']==0 and len(harness['negativeGuards'])==6
      and harness['harness']['qualitySemanticsUnchanged'] and harness['oldTwelveGuardHarnessBytesNotSubstituted'],
      'new one-dependency quality invariance, not old harness input substitution')
    contract=json.loads((review.host.BASE/review.PINS['contract'][0]).read_bytes())
    inputs={'tools/quality/harnesses/monitoring-api-jobs-pom.xml':harness['afterHarnessSha256'],
      'tools/quality/harnesses/monitoring-pom.xml':contract['harness']['knownBatchSha256'],
      'src/schubert-nk-api/pom.xml':contract['apiPom']['sha256'],contract['canonicalDdl']['path']:contract['canonicalDdl']['sha256']}
    for path,digest in inputs.items():review.require(hashlib.sha256(blob(path)).hexdigest()==digest,'each declared current input byte bound to proper original witness')
    observation_path='src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/monitoring/DbPoolMetricObservation.java'
    code=blob(observation_path).decode()
    calls=re.findall(r'\b(pool|config)\.([A-Za-z]+)\(',code)
    review.require(calls==[('pool','getActiveConnections'),('pool','getIdleConnections'),('pool','getThreadsAwaitingConnection'),('config','getMaximumPoolSize')],
      'exact four getter calls only, no config credentials/management controls')
    review.require(not re.search(r'HikariDataSource|new HikariConfig|ManagementFactory|MBeanServer|softEvict|suspendPool|resumePool',code),
      'no pool/config construction, management lookup or pool control in observation')
    review.EXTRA_REVIEW=dict(harnessWitness=dict(path=harness_path,sha256=harness_sha),contractInputHashes=inputs,
      newPoolObservationRawFindings=0,newCollectorRawFindings=3,readonlyGetterCalls=calls,
      actualPoolOrConfigCreated=0,actualManagementOperations=0,allPrevious71SourceBytesUnchanged=True)
    review.main()
