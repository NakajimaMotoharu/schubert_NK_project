"""Current24/static five exact dispositions/fixture-only BUG1659 correction; no runtime operations."""
import copy
import hashlib
import json
import subprocess
import pg7310_api_async_metric_review as review
import pg7324_api_async_count_review as previous
import pg7344_api_collector_owned_registry_six_compile as compilation

ROOT=review.host.ROOT
COUNT_TEST='src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/AsyncJobCountRepositoryTest.java'
COLLECTOR_TEST='src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/monitoring/AsyncJobMetricCollectorTest.java'

def blob(source,path):
    return subprocess.check_output(['git','show',source+':'+path],cwd=ROOT)

def fixture_contract(count_before,count_after,collector_before,collector_after):
    expected=count_before.decode()
    for before,after in (
      ('  private record Row(', '  record Row('),
      ('  private static final class Fixture {','  static final class Fixture {'),
      ('    int cursor = -1;\n','    int cursor = -1;\n    Runnable beforeStatementClose = () -> {};\n'),
      ('                    closes.add("PS");','                    beforeStatementClose.run();\n                    closes.add("PS");')):
        review.require(expected.count(before)==1,'one exact owned fixture boundary')
        expected=expected.replace(before,after)
    review.require(expected.encode()==count_after,'only two fixture visibility changes and owned before-close oracle hook')
    source=collector_before.decode()
    declaration='class AsyncJobMetricCollectorTest {\n'
    adapter='''  private static final class Registry extends SimpleMeterRegistry implements AutoCloseable {
    @Override
    public void close() {
      super.close();
    }
  }

'''
    review.require(source.count(declaration)==1 and source.count('new SimpleMeterRegistry()')==9,
      'all nine originally failing owned registry constructions')
    expected=source.replace(declaration,declaration+adapter).replace('new SimpleMeterRegistry()','new Registry()')
    review.require(expected.encode()==collector_after,'only explicit close adapter/all nine allocations, every original assertion byte unchanged')

def classify(current):
    raw=current['staticRaw']['pmd']
    review.require(raw['actualExit']==4 and raw['processingErrors']==0 and len(raw['findings'])==5,'all five actual PMD findings')
    inherited=copy.deepcopy(current)
    inherited['staticRaw']['pmd']['findings']=[r for r in raw['findings'] if r['class']=='AsyncJobCountRepository']
    previous.compilation=compilation
    result=previous.classify(inherited)
    path='src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/monitoring/AsyncJobMetricCollector.java'
    source=blob(compilation.SOURCE,path)
    review.require(hashlib.sha256(source).hexdigest()==current['sourceFiles'][path], 'original executed collector bytes')
    compact=''.join(source.decode().split())
    review.require('privatefinalObjectlock=newObject();' in compact and 'synchronized(lock){' in compact
      and 'catch(SQLException|RuntimeException|ErrorfailedObservation){metrics.missing();throwfailedObservation;}' in compact,
      'private owner monitor and fail-closed rethrow exact, not swallow/normalization')
    expected={('AvoidSynchronizedStatement','29','5'),('AvoidCatchingGenericException','35','31'),('AvoidCatchingGenericException','35','50')}
    seen=set()
    for row in raw['findings']:
        if row['class']=='AsyncJobCountRepository':continue
        key=(row.get('rule'),row.get('beginline'),row.get('begincolumn'))
        review.require(key in expected and key not in seen and row.get('class')=='AsyncJobMetricCollector'
          and row.get('method')=='collect' and row.get('package')=='dev.codex.schubert.nk.api.monitoring',
          'only three exact private-sync/rethrow context rows')
        seen.add(key)
        result.append(dict(raw=row,classification='CONTEXT_NOT_APPLICABLE',sourcePath=path,
          sourceSha256=current['sourceFiles'][path],reason='411 private lock serializes one owner read/close/publication; catch only marks unknown then rethrows same checked/runtime/fatal, no normal failure result',
          ordinaryTestWitness='PG7340-api-collector-owned-registry-host-v1:ASYNCCONN003/006/008',
          sourceOrRulesChanged=False,suppressionAdded=False))
    review.require(seen==expected,'all new rows individually classified, no broad rule suppression')
    return result

if __name__=='__main__':
    review.SOURCE=compilation.SOURCE;review.OUT=review.host.BASE/'PG7338-api-async-collector-review-v1'
    review.CURRENT_TESTS=24;review.CURRENT_SUITES=3;review.CURRENT_EXECUTABLE=5
    review.PHYSICAL_COUNT=1728;review.ADDED_PHYSICAL=59;review.PREVIOUS_COUNT=67
    review.INTRODUCED_COUNT=2;review.CHANGED_COUNT=1;review.STATIC_CLASSIFIER=classify
    review.PINS=dict(review.PINS)
    for key,path in {
      'currentApi':'PG7342-api-collector-owned-registry-post-v1/manifest.json',
      'physical':'PG7334-api-async-collector-six-post-v1/manifest.json',
      'trace':'PG7336-api-async-collector-trace-v1/manifest.json',
      'previous':'PG7322-api-async-count-trace-v1/manifest.json'}.items():
        review.PINS[key]=(path,review.host.sha(review.host.BASE/path))
    count_before=blob('faf7b0756d5a4fbb4098c17c2667ee7cf54b585c',COUNT_TEST)
    count_after=blob(compilation.SOURCE,COUNT_TEST)
    collector_before=blob('d791e5c8dc940aea673da42032b11a4d6ee55b8e',COLLECTOR_TEST)
    collector_after=blob(compilation.SOURCE,COLLECTOR_TEST)
    fixture_contract(count_before,count_after,collector_before,collector_after)
    guards=[]
    for label in ('oracle-change','close-hook-removed','allocation-unfixed','adapter-close-removed'):
        count=count_after;collector=collector_after
        if label=='oracle-change':count=count.replace(b'assertEquals(15,',b'assertEquals(16,',1)
        elif label=='close-hook-removed':count=count.replace(b'beforeStatementClose.run();',b'',1)
        elif label=='allocation-unfixed':collector=collector.replace(b'new Registry()',b'new SimpleMeterRegistry()',1)
        else:collector=collector.replace(b'super.close();',b'',1)
        try:fixture_contract(count_before,count,collector_before,collector)
        except ValueError:guards.append(dict(kind=label,rejected=True))
        else:raise ValueError('fixture oracle/lifetime mutation accepted')
    contract=json.loads((review.host.BASE/review.PINS['contract'][0]).read_bytes())
    inputs={'tools/quality/harnesses/monitoring-api-jobs-pom.xml':contract['harness']['apiSha256'],
      'tools/quality/harnesses/monitoring-pom.xml':contract['harness']['knownBatchSha256'],
      'src/schubert-nk-api/pom.xml':contract['apiPom']['sha256'],contract['canonicalDdl']['path']:contract['canonicalDdl']['sha256']}
    for path,digest in inputs.items():
        review.require(hashlib.sha256(blob(compilation.SOURCE,path)).hexdigest()==digest,'same original twelve-guard inputs only')
    review.EXTRA_REVIEW=dict(fixtureNegativeGuards=guards,borrowedFixtureOracleUnchanged=True,
      adapterConstructionsFixed=9,productionSourceUnchangedByBugFix=True,contractInputHashes=inputs,
      relatedBug='BUG-1659',relatedExpansion='YKT-1412')
    review.main()
