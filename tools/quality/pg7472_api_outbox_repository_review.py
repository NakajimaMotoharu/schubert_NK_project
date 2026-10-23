"""Current90/19 source-domain review; two exact TWR false positives, new Snapshot five contracts."""
import copy
import hashlib
import json
import re
import subprocess
import pg7310_api_async_metric_review as review
import pg7372_api_pool_observation_review as previous
import pg7458_api_outbox_age_review as age
import pg7462_api_outbox_repository_host as execution
import pg7466_api_outbox_repository_six_compile as compilation

MAIN='src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/monitoring/persistence/OutboxObservationRepository.java'

def blob(path):
    return subprocess.check_output(['git','show',compilation.SOURCE+':'+path],cwd=review.host.ROOT)

def classify(current):
    raw=current['staticRaw']['pmd'];review.require(raw['actualExit']==4 and raw['processingErrors']==0 and len(raw['findings'])==10,'exact ten current raw findings')
    carried=copy.deepcopy(current);carried['staticRaw']['pmd']['findings']=[r for r in raw['findings'] if r['class']!='OutboxObservationRepository']
    previous.compilation=compilation;result=previous.classify(carried);seen=set();source=blob(MAIN);compact=''.join(source.decode().split())
    review.require(hashlib.sha256(source).hexdigest()==current['sourceFiles'][MAIN]
      and 'try(statement){' in compact and 'try(rows){' in compact,'exact current issue-bearing byte and two existing-variable TWR scopes')
    expected={('statement','47','33'),('rows','51','27')}
    for row in raw['findings']:
        if row['class']!='OutboxObservationRepository':continue
        key=(row.get('variable'),row.get('beginline'),row.get('begincolumn'))
        review.require(key in expected and key not in seen and row['rule']=='CloseResource' and row['method']=='read'
          and row['package']=='dev.codex.schubert.nk.api.monitoring.persistence','only exact two TWR false-positive rows')
        seen.add(key);result.append(dict(raw=row,classification='FALSE_POSITIVE',sourcePath=MAIN,sourceSha256=current['sourceFiles'][MAIN],
          reason='Java existing-variable TWR; null acquisition rejected before ownership, all acquired RS then PS close on success/read/timeout/Runtime/Error/close failure. OUTBOXDB001/007/008 independently verify exact close identity/order and suppressed faults.',
          ordinaryTestWitness='PG7462-api-outbox-repository-host-v1',sourceOrRulesChanged=False,suppressionAdded=False))
    review.require(seen==expected,'every fresh row individually classified, no broad rule suppression')
    return result

if __name__=='__main__':
    review.SOURCE=compilation.SOURCE;review.OUT=review.host.BASE/'PG7472-api-outbox-repository-review-v1'
    review.CURRENT_TESTS=90;review.CURRENT_SUITES=11;review.CURRENT_EXECUTABLE=19
    review.PHYSICAL_COUNT=1742;review.ADDED_PHYSICAL=73
    review.PREVIOUS_COUNT=84;review.INTRODUCED_COUNT=2;review.CHANGED_COUNT=0;review.STATIC_CLASSIFIER=classify
    review.PINS=dict(review.PINS)
    for key,path in {'currentApi':'PG7464-api-outbox-repository-post-v1/manifest.json',
      'physical':'PG7468-api-outbox-repository-six-post-v1/manifest.json',
      'trace':'PG7470-api-outbox-repository-trace-v1/manifest.json',
      'previous':'PG7456-api-outbox-age-trace-v1/manifest.json'}.items():review.PINS[key]=(path,review.host.sha(review.host.BASE/path))
    current=json.loads((review.host.BASE/review.PINS['currentApi'][0]).read_bytes())
    raw=json.loads((execution.SLOT/'manifest.safe.json').read_bytes())
    cases=[r for r in raw['cases'] if r['classname'].endswith('.OutboxObservationRepositoryTest')]
    review.require(len(cases)==10 and all(r['result']=='PASS' for r in cases),'all ten actual independent new cases, not definitions')
    source=blob(MAIN).decode();compact=''.join(source.split())
    review.require('"SELECTstatus,COUNT(*)ASrow_count,MIN(created_at)ASoldest_created_at"+"FROMschubert.mq_outboxGROUPBYstatus"' in compact
      and 'rows.getObject("oldest_created_at",OffsetDateTime.class)' in compact
      and not re.search(r'\.getTimestamp\(|\.setTimestamp\(|\.commit\(|\.rollback\(|\.setAutoCommit\(|\.setReadOnly\(|\.setTransactionIsolation\(',source),
      'canonical fixed projection/typed timestamp and no borrowed transaction mutation')
    name='dev/codex/schubert/nk/api/monitoring/persistence/OutboxObservationRepository$Snapshot'
    classes=execution.SLOT/'snapshot/tools/quality/harnesses/target/classes';file=classes/(name+'.class')
    review.require(review.host.sha(file)==current['physicalClasses'][name+'.class'],'actual new executed record byte')
    command=[str(review.host.TC/'jdk-25.0.4/bin/javap'),'-p','-c','-v','-classpath',str(classes),name.replace('/','.')]
    done=subprocess.run(command,capture_output=True,text=True);text=done.stdout
    methods=['equals(java.lang.Object)','hashCode()','toString()','counts()','ages()']
    review.require(done.returncode==0 and 'java/lang/runtime/ObjectMethods.bootstrap' in text
      and all(m+';' in text for m in methods) and all(re.search(r'REF_getField\s+[^\s]+\.'+field+r':Ldev/codex/schubert/nk/api/monitoring/'+re.escape(owner)+r';',text)
      for field,owner in (('counts','OutboxRowsMetricRecorder$Counts'),('ages','OutboxAgeMetricRecorder$Ages'))),'all five generated methods and every actual reference field in bootstrap')
    age_path='PG7458-api-outbox-age-review-v1/manifest.json'
    review.require(review.host.sha(review.host.BASE/age_path)=='695ead7f1e6fdb79baeac9633b6c283a13b4867e4448d4fcee8318a903b2fa24','original age/contract provenance')
    prior=json.loads((review.host.BASE/age_path).read_bytes());extra=prior['additionalReview'];record=extra['newRecordGeneratedContract']
    review.require(current['physicalClasses'].get(record['className']+'.class')==record['sha256'],'prior new Age generated6 exact bytes')
    age.projection(blob(age.METRIC))
    for path,digest in extra['contractInputHashes'].items():review.require(hashlib.sha256(blob(path)).hexdigest()==digest,'all original contract inputs exact current bytes')
    platform_path=extra['previousGenerated21ByteProof']['path']
    review.require(review.host.sha(review.host.BASE/platform_path)==extra['previousGenerated21ByteProof']['sha256'],'original platform/static proof')
    platform=json.loads((review.host.BASE/platform_path).read_bytes())
    for row in platform['generatedTypes']:review.require(current['physicalClasses'].get(row['className']+'.class')==row['sha256'],'all prior21 generated contracts same actual Main bytes')
    review.require(review.host.sha(review.host.TC/'jdk-25.0.4/lib/modules')==platform['jdkModulesSha256']
      and review.host.sha(review.host.TC/'m2/repository/org/jacoco/org.jacoco.core/0.8.15/org.jacoco.core-0.8.15.jar')==platform['jacocoCoreSha256'],
      'same actual JDK/official filter static bytes, no old PT transfer')
    for simple,expected in (('GeneratedMetricValueContractTest',8),('OutboxAgeMetricRecorderTest',8)):
        group=[r for r in raw['cases'] if r['classname'].endswith('.'+simple)]
        review.require(len(group)==expected and all(r['result']=='PASS' for r in group),'current source generated contract cases actually executed')
    review.EXTRA_REVIEW=dict(newRepositoryProjection='status COUNT(*) MIN(created_at), borrowed readonly RC; timeout1s; typed OffsetDateTime, no connection/transaction lifetime ownership',
      newTwrFalsePositives=2,newSnapshotGeneratedContract=dict(className=name,sha256=review.host.sha(file),methods=methods,testIds=['OUTBOXDB010'],
        command=command,actualExit=0,stdoutSha256=hashlib.sha256(done.stdout.encode()).hexdigest(),stderrSha256=hashlib.sha256(done.stderr.encode()).hexdigest(),
        independentHash=96447,independentFormula='31*3045 + 2052; nested component values fixed by independent primitive/JDK Duration vectors'),
      currentApiGeneratedTypes=8,currentApiGeneratedMethodsSeparatelyVerifiedNotAddedToCounters=32,customExclusionsAdded=False,
      originalAgeProof=dict(path=age_path,sha256=review.host.sha(review.host.BASE/age_path)),contractInputHashes=extra['contractInputHashes'],
      actualDatabaseOrDispatcherActions=0,actualDriverOrAsOfAdmissionAccepted=False,whole451Accepted=False)
    review.main()
