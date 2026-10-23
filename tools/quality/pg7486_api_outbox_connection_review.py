"""Current98 exact quality/domain review; owner lock and unchanged-failure unknown marking contexts."""
import copy
import hashlib
import json
import subprocess
import pg7310_api_async_metric_review as review
import pg7472_api_outbox_repository_review as previous
import pg7476_api_outbox_connection_host as execution
import pg7480_api_outbox_connection_six_compile as compilation

MAIN='src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/monitoring/OutboxMetricCollector.java'

def blob(path):
    return subprocess.check_output(['git','show',compilation.SOURCE+':'+path],cwd=review.host.ROOT)

def classify(current):
    raw=current['staticRaw']['pmd'];review.require(raw['actualExit']==4 and raw['processingErrors']==0 and len(raw['findings'])==13,'all thirteen actual raw rows')
    carried=copy.deepcopy(current);carried['staticRaw']['pmd']['findings']=[r for r in raw['findings'] if r['class']!='OutboxMetricCollector']
    previous.compilation=compilation;result=previous.classify(carried)
    source=blob(MAIN);compact=''.join(source.decode().split());seen=set()
    review.require(hashlib.sha256(source).hexdigest()==current['sourceFiles'][MAIN]
      and 'privatefinalObjectlock=newObject();' in compact and 'synchronized(lock){' in compact
      and 'catch(SQLException|RuntimeException|ErrorfailedObservation){rows.missing();ages.missing();lastObservation.set(Optional.empty());throwfailedObservation;}' in compact,
      'private owner lock and all-family unknown marking followed by unchanged failure throw, not normalization')
    expected={('AvoidSynchronizedStatement','33','5'),('AvoidCatchingGenericException','41','31'),('AvoidCatchingGenericException','41','50')}
    for row in raw['findings']:
        if row['class']!='OutboxMetricCollector':continue
        key=(row.get('rule'),row.get('beginline'),row.get('begincolumn'))
        review.require(key in expected and key not in seen and row['method']=='collect'
          and row['package']=='dev.codex.schubert.nk.api.monitoring','exact three private owner/failure context rows')
        seen.add(key);result.append(dict(raw=row,classification='CONTEXT_NOT_APPLICABLE',sourcePath=MAIN,sourceSha256=current['sourceFiles'][MAIN],
          reason='411 private one-owner read/complete-close/publication serialization; failure marks both supplied metric families and immutable owner snapshot unknown then rethrows same SQL/Runtime/Error. OUTBOXCONN001/003/006 verify close timing/identity/ordering. No normal failure result or public monitor.',
          ordinaryTestWitness='PG7476-api-outbox-connection-host-v1',sourceOrRulesChanged=False,suppressionAdded=False))
    review.require(seen==expected,'all new rows individually reasoned, no generic rule suppression')
    return result

if __name__=='__main__':
    review.SOURCE=compilation.SOURCE;review.OUT=review.host.BASE/'PG7486-api-outbox-connection-review-v1'
    review.CURRENT_TESTS=98;review.CURRENT_SUITES=12;review.CURRENT_EXECUTABLE=20
    review.PHYSICAL_COUNT=1743;review.ADDED_PHYSICAL=74
    review.PREVIOUS_COUNT=86;review.INTRODUCED_COUNT=2;review.CHANGED_COUNT=0;review.STATIC_CLASSIFIER=classify
    review.PINS=dict(review.PINS)
    for key,path in {'currentApi':'PG7478-api-outbox-connection-post-v1/manifest.json',
      'physical':'PG7482-api-outbox-connection-six-post-v1/manifest.json',
      'trace':'PG7484-api-outbox-connection-trace-v1/manifest.json',
      'previous':'PG7470-api-outbox-repository-trace-v1/manifest.json'}.items():review.PINS[key]=(path,review.host.sha(review.host.BASE/path))
    current=json.loads((review.host.BASE/review.PINS['currentApi'][0]).read_bytes())
    raw=json.loads((execution.SLOT/'manifest.safe.json').read_bytes());cases=[r for r in raw['cases'] if r['classname'].endswith('.OutboxMetricCollectorTest')]
    review.require(len(cases)==8 and all(r['result']=='PASS' for r in cases),'actual new eight connection cases, not definitions')
    source=''.join(blob(MAIN).decode().split())
    ordered=['Snapshot supplied = repository.read(connection, asOf);','rows.record(supplied.counts());',
      'ages.record(supplied.ages());','lastObservation.set(Optional.of(supplied));']
    offsets=[source.index(''.join(s.split())) for s in ordered]
    review.require(offsets==sorted(offsets) and len(set(offsets))==4,'one read completes before both publications and owner snapshot')
    require_null='Objects.requireNonNull(asOf,"outboxobservationinstant");'
    review.require(source.index(require_null)<source.index('synchronized(lock){')
      and source.index('if(!rows.detailedMetricsRequested())returnOptional.empty();')<offsets[0],
      'boundary null before owner mutation; STANDARD branch before any detailed query')
    prior_path='PG7472-api-outbox-repository-review-v1/manifest.json'
    review.require(review.host.sha(review.host.BASE/prior_path)=='4ff38f5b8f8a6cf7bff58ae3667f14ff87f43d4060fd33efd0bb3742b05dfaa2','original same-method generated/contract proof')
    prior=json.loads((review.host.BASE/prior_path).read_bytes())['additionalReview'];snapshot=prior['newSnapshotGeneratedContract']
    review.require(current['physicalClasses'].get(snapshot['className']+'.class')==snapshot['sha256'],'actual unchanged Snapshot generated5 byte identity')
    age_ref=prior['originalAgeProof'];review.require(review.host.sha(review.host.BASE/age_ref['path'])==age_ref['sha256'],'original Age six-method provenance')
    age=json.loads((review.host.BASE/age_ref['path']).read_bytes())['additionalReview'];record=age['newRecordGeneratedContract']
    review.require(current['physicalClasses'].get(record['className']+'.class')==record['sha256'],'actual unchanged Age generated6 byte')
    platform_ref=age['previousGenerated21ByteProof'];review.require(review.host.sha(review.host.BASE/platform_ref['path'])==platform_ref['sha256'],'original generated21/platform proof')
    platform=json.loads((review.host.BASE/platform_ref['path']).read_bytes())
    for row in platform['generatedTypes']:review.require(current['physicalClasses'].get(row['className']+'.class')==row['sha256'],'actual previous21 exact Main bytes')
    review.require(review.host.sha(review.host.TC/'jdk-25.0.4/lib/modules')==platform['jdkModulesSha256']
      and review.host.sha(review.host.TC/'m2/repository/org/jacoco/org.jacoco.core/0.8.15/org.jacoco.core-0.8.15.jar')==platform['jacocoCoreSha256'],'same inspected JDK/official filter static bytes')
    for simple,count in (('GeneratedMetricValueContractTest',8),('OutboxAgeMetricRecorderTest',8),('OutboxObservationRepositoryTest',10)):
        group=[r for r in raw['cases'] if r['classname'].endswith('.'+simple)]
        review.require(len(group)==count and all(r['result']=='PASS' for r in group),'all current source generated value contract ordinary cases really executed')
    for path,digest in prior['contractInputHashes'].items():review.require(hashlib.sha256(blob(path)).hexdigest()==digest,'each contract input same byte before static proof reuse')
    review.EXTRA_REVIEW=dict(readClosePublicationOffsets=offsets,privateOneOwnerLock=True,standardDetailedQueryInvoked=False,
      actualDatabaseOrDispatcherActions=0,crossFamilyAtomicScrapeClaim=False,currentApiGeneratedTypes=8,
      currentApiGeneratedMethodsSeparatelyVerifiedNotAddedToCounters=32,customExclusionsAdded=False,
      contractInputHashes=prior['contractInputHashes'],priorGeneratedProof=dict(path=prior_path,sha256=review.host.sha(review.host.BASE/prior_path)),
      actualSourceRoleDriverAsOfOrOuterDeadlineAccepted=False,allPrevious86SourceBytesUnchanged=True)
    review.main()
