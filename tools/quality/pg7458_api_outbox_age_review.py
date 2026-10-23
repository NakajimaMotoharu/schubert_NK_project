"""Current80 same-source quality/domain review and six new generated Duration contracts."""
import hashlib
import json
import re
import subprocess
import pg7310_api_async_metric_review as review
import pg7372_api_pool_observation_review as previous
import pg7400_api_outbox_rows_review as outbox
import pg7448_api_outbox_age_host as execution
import pg7452_api_outbox_age_six_compile as compilation

METRIC='src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/monitoring/OutboxAgeMetricRecorder.java'

def blob(path):
    return subprocess.check_output(['git','show',compilation.SOURCE+':'+path],cwd=review.host.ROOT)

def projection(code):
    compact=''.join(code.decode().split())
    review.require('importdev.codex.schubert.nk.api.monitoring.OutboxRowsMetricRecorder.Status;' in compact
      and 'Gauge.builder("nk_outbox_oldest_seconds",' in compact
      and re.findall(r'\.tag\(([^)]+)\)',compact)==['"store","API"','"status",status.name(']
      and 'returnage.getSeconds()+age.getNano()/1_000_000_000d;' in compact,
      'exact existing enum/API-only closed label set and nonoverflowing seconds conversion')
    return dict(store='API',statuses=['PENDING','SENT','ERROR'],metric='nk_outbox_oldest_seconds',labels=['store','status'],
      conversion='Duration seconds + nanosecond fraction, no long multiply; actual derivation not implemented')

if __name__=='__main__':
    review.SOURCE=compilation.SOURCE;review.OUT=review.host.BASE/'PG7458-api-outbox-age-review-v1'
    review.CURRENT_TESTS=80;review.CURRENT_SUITES=10;review.CURRENT_EXECUTABLE=17
    review.PHYSICAL_COUNT=1740;review.ADDED_PHYSICAL=71
    review.PREVIOUS_COUNT=82;review.INTRODUCED_COUNT=2;review.CHANGED_COUNT=0
    previous.compilation=compilation;review.STATIC_CLASSIFIER=previous.classify
    review.PINS=dict(review.PINS)
    for key,path in {
      'currentApi':'PG7450-api-outbox-age-post-v1/manifest.json',
      'physical':'PG7454-api-outbox-age-six-post-v1/manifest.json',
      'trace':'PG7456-api-outbox-age-trace-v1/manifest.json',
      'previous':'PG7442-web-generated-byte-trace-v1/manifest.json'}.items():
        review.PINS[key]=(path,review.host.sha(review.host.BASE/path))
    current=json.loads((review.host.BASE/review.PINS['currentApi'][0]).read_bytes())
    review.require(not any(r['class'].startswith('OutboxAgeMetricRecorder') for r in current['staticRaw']['pmd']['findings']),
      'all new Main/nested raw findings zero, no inherited reason for new code')
    metric=blob(METRIC);age_projection=projection(metric);guards=[]
    for kind in ('wrong-store','actor-label','wrong-unit','overflow-conversion'):
        changed=metric
        if kind=='wrong-store':changed=changed.replace(b'.tag("store", "API")',b'.tag("store", "WEB")')
        elif kind=='actor-label':changed=changed.replace(b'.tag("status",',b'.tag("actor",')
        elif kind=='wrong-unit':changed=changed.replace(b'nk_outbox_oldest_seconds',b'nk_outbox_oldest_milliseconds')
        else:changed=changed.replace(b'age.getSeconds() + age.getNano() / 1_000_000_000d',b'age.toNanos() / 1_000_000_000d')
        review.require(changed!=metric,'each negative mutation actually changes exact current source')
        try:projection(changed)
        except ValueError:guards.append(dict(kind=kind,rejected=True))
        else:raise ValueError('unsafe age metric projection accepted')
    rows_projection=outbox.projection(blob(outbox.DDL),blob(outbox.METRIC))
    review.require(blob(outbox.DDL)==subprocess.check_output(['git','show','e7d64fda2453e906ee6ccc5fe718e5c29841e4aa:'+outbox.DDL],cwd=review.host.ROOT),
      'canonical three-state DDL unchanged, no migration rewrite')
    raw=json.loads((execution.SLOT/'manifest.safe.json').read_bytes())
    cases=[r for r in raw['cases'] if r['classname'].endswith('.OutboxAgeMetricRecorderTest')]
    review.require(len(cases)==8 and all(r['result']=='PASS' for r in cases)
      and any(r['name']=='outboxAge008SeparateOwnersAndGeneratedValueContractsAreExact' for r in cases),'all eight actual new cases including generated contract oracle')
    prefix='dev/codex/schubert/nk/api/monitoring/';name=prefix+'OutboxAgeMetricRecorder$Ages'
    classes=execution.SLOT/'snapshot/tools/quality/harnesses/target/classes';file=classes/(name+'.class')
    review.require(review.host.sha(file)==current['physicalClasses'][name+'.class'],'actual executed new record bytes')
    command=[str(review.host.TC/'jdk-25.0.4/bin/javap'),'-p','-c','-v','-classpath',str(classes),name.replace('/','.')]
    done=subprocess.run(command,capture_output=True,text=True);text=done.stdout
    review.require(done.returncode==0 and 'java/lang/runtime/ObjectMethods.bootstrap' in text,'noninitializing javap actual JDK record generator')
    methods=['equals(java.lang.Object)','hashCode()','toString()','pending()','sent()','error()']
    review.require(all(m+';' in text for m in methods) and all(re.search(r'REF_getField\s+[^\s]+\.'+field+r':Ljava/time/Duration;',text)
      for field in ('pending','sent','error')),'all six generated methods and every actual reference field participates')
    platform_path='PG7413-api-generated-value-review-v2/manifest.json'
    review.require(review.host.sha(review.host.BASE/platform_path)=='7d108ca7499763b5ed5526e60144276ace055c66aa88e380a0ccde0a3be2a82e','original platform/filter byte proof')
    platform=json.loads((review.host.BASE/platform_path).read_bytes())
    jacoco=review.host.TC/'m2/repository/org/jacoco/org.jacoco.core/0.8.15/org.jacoco.core-0.8.15.jar'
    review.require(review.host.sha(review.host.TC/'jdk-25.0.4/lib/modules')==platform['jdkModulesSha256']
      and review.host.sha(jacoco)==platform['jacocoCoreSha256'],'same actual installed JDK and official preexisting filter bytes')
    for row in platform['generatedTypes']:
        review.require(current['physicalClasses'].get(row['className']+'.class')==row['sha256'],'all previous21 API generated contracts exact Main bytes')
    oldgen=[r for r in raw['cases'] if r['classname'].endswith('.GeneratedMetricValueContractTest')]
    review.require(len(oldgen)==8 and all(r['result']=='PASS' for r in oldgen),'current source actually reruns own generated8, not historical success transfer')
    harness_path='PG7369-api-pool-harness-review-v1/manifest.json'
    review.require(review.host.sha(review.host.BASE/harness_path)=='b7901dc09260aaa9b88109face329921a65236e3e6c7969eccd11bea987cfab4','original actual harness invariance')
    harness=json.loads((review.host.BASE/harness_path).read_bytes())
    contract=json.loads((review.host.BASE/review.PINS['contract'][0]).read_bytes())
    inputs={'tools/quality/harnesses/monitoring-api-jobs-pom.xml':harness['afterHarnessSha256'],
      'tools/quality/harnesses/monitoring-pom.xml':contract['harness']['knownBatchSha256'],
      'src/schubert-nk-api/pom.xml':contract['apiPom']['sha256'],outbox.DDL:contract['canonicalDdl']['sha256']}
    for path,digest in inputs.items():review.require(hashlib.sha256(blob(path)).hexdigest()==digest,'each current input to proper original quality witness')
    review.EXTRA_REVIEW=dict(ageProjection=age_projection,projectionNegativeGuards=guards,rowsProjection=rows_projection,
      newRecordGeneratedContract=dict(className=name,sha256=review.host.sha(file),methods=methods,testIds=['OUTBOXAGE008'],
        command=command,actualExit=0,stdoutSha256=hashlib.sha256(done.stdout.encode()).hexdigest(),stderrSha256=hashlib.sha256(done.stderr.encode()).hexdigest(),
        independentHash=3045,fixedText='Ages[pending=PT3S, sent=PT5S, error=PT7S]',customExclusionAdded=False),
      currentApiGeneratedTypes=7,currentApiGeneratedMethodsSeparatelyVerifiedNotAddedToCounters=27,
      previousGenerated21ByteProof=dict(path=platform_path,sha256=review.host.sha(review.host.BASE/platform_path)),
      contractInputHashes=inputs,newAgeMetricRawFindings=0,actualDatabaseOrDispatcherActions=0,
      actualOldestDerivationAccepted=False,webStoreAccepted=False,allPrevious82SourceBytesUnchanged=True)
    review.main()
