"""Original whole six eligibility, non-returning SQL callbacks, constructor-only callees and fixture preservation."""
from pathlib import Path
import datetime
import hashlib
import json
import re
import zipfile

R=Path.cwd();B=R/'evidence/01_PT/005_NK-MSG-001';C=B/'input/042_owned_outbox_bounded_scope.json';load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();cfg=load(C);RUNS=R.parent/'pgpt-runs/PG379';O=R/cfg['preflightManifest'];assert not O.parent.exists()
pre=load(RUNS/cfg['compileSlot']/'manifest.json');sta=load(RUNS/cfg['staticSlot']/'manifest.json');assert pre['actualExit']==0 and pre['inputHashes']==sta['inputHashes']
for name,h in pre['inputHashes'].items():assert sha(R/name)==h
path=next(iter(cfg['testClasses']));new=(R/path).read_text();old=(R/cfg['before']).read_text()
tok=lambda s:''.join(re.findall(r'"(?:\\.|[^"\\])*"|\S',s))
assert '"""' not in new+old
prefix='try(varexecutor=Executors.newSingleThreadExecutor()){';tail='}finally{release.countDown();owned.close();}'
a=tok(old);start=a.index(prefix)+len(prefix);end=a.index(tail,start);expected=a[:start]+'try{'+a[start:end]+'}finally{release.countDown();}'+a[end:]
for name in ['release','gate']:
    before=name+'.await();';after='assertTrue('+name+'.await(5,TimeUnit.SECONDS));';assert expected.count(before)==1;expected=expected.replace(before,after,1)
assert tok(new)==expected
negative=[]
for before,after in [('assertTrue(release.await(5, TimeUnit.SECONDS));','release.await();'),('assertTrue(gate.await(5, TimeUnit.SECONDS));','gate.await();'),('closing.get(50, TimeUnit.MILLISECONDS)','closing.get(5, TimeUnit.MILLISECONDS)'),('assertTrue(closing.get(3, TimeUnit.SECONDS));','assertFalse(closing.get(3, TimeUnit.SECONDS));'),('"NK_API_OUTBOX_FATAL"','"BAD_OUTBOX_FATAL"')]:
    assert before in new and tok(new.replace(before,after,1))!=expected;negative.append(before)
assert tok(new).count('}finally{release.countDown();}}finally{release.countDown();owned.close();}')==1
methods=re.findall(r'@Test\s+void\s+(\w+)\s*\(',new);assert len(methods)==len(set(methods))==6
assert tok(new).count('dispatcher(()->{')==9
assert 'return null;' not in new and 'java.sql.Connection' not in new
assert not any(s in new for s in ['@Before','@After','@Disabled','@TempDir','@ExtendWith','java.net.','java.nio.file','ProcessBuilder','Class.forName','ServiceLoader','DriverManager','setAccessible','TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException'])
factory='return new OutboxDispatcher(open, () -> { throw new AssertionError("JMS must not open without DB claim"); }, new JdbcOutboxRepository(() -> 0), new OutboxJmsSender(), Clock.systemUTC());'
assert tok(factory) in tok(new)
# These are source-reviewed fixed fixture contracts, not a new callback implementation.
callbacks=[dict(id='graph322-fatal-six-kinds',result='throws SQLException or RuntimeException graph'),dict(id='graph322-ordinary-cycle',result='throws RuntimeException'),dict(id='outbox005-assembly',result='throws SQLException'),dict(id='outbox001-ordinary-sql-runtime',result='throws SQLException or RuntimeException'),dict(id='outbox001-invalid-constructor',result='throws SQLException if called; rejected constructor before start'),dict(id='outbox002-in-flight',result='finite release then throws SQLException; timeout assertion also throws Error'),dict(id='outbox003-fatal',result='throws exact supplied Error'),dict(id='outbox004-interrupt',result='sets own worker interrupt then throws SQLException'),dict(id='outbox004-self-join',result='finite gate/assert rejected self-close then throws SQLException')]
assert len(callbacks)==9
assert not sta['reports']['checkstyle']['items'] and not sta['reports']['checkstyle']['processingErrors'] and not sta['reports']['pmd']['processingErrors']
items=sta['reports']['pmd']['items'];expected_sites={('CloseResource',26),('CloseResource',146),('CloseResource',236)}|{('DoNotUseThreads',n) for n in [35,40,202,207,211,213,215,216,265,270,272,283,285,287,301]}
assert len(items)==18 and {(r['rule'],int(r['beginline'])) for r in items}==expected_sites
assert sta['stages']['pmd']['actualExit']==4 and sta['stages']['checkstyle']['actualExit']==0
classifications=[]
for row in items:
    if row['rule']=='CloseResource':
        reason=('ByteArrayOutputStream is only a memory sink; owning PrintStream uses TWR and closes it even on assertion failure, System.err is restored in outer finally.' if row['beginline'] in ['26','236'] else 'Unstarted OwnedOutboxDispatcher is closed immediately and twice, then restart rejection/health are the actual oracle. No worker starts before the first close; use-after-close is an intentional state assertion, not a reopened resource.')
    else:reason='JUnit-only owned worker/thread/interrupt and finite latch/Future observations, outside J2EE. Original close stop/interrupt/self-join ownership is under test; all callback waits now finite, inner finally releases before joining executor, outer finally closes worker.'
    classifications.append(dict(finding=row,applicableViolation=False,reason=reason))
normal=RUNS/'pg22084-api-stop-state-six-main-compile-v1/manifest.safe.json';assert sha(normal)=='b2f07209804d71ee2ffbc4d9aca5311d4e6cf15721c74bcde411f86538cf4f27';nm=load(normal);assert nm['source']=='7aed8eace7c844c2f79f2e39db766faf914890d5'
for p,h in pre['dependencies'].items():assert sha(Path(p))==h
for module in cfg['modules']:assert sha(Path(nm['jars'][module]['path']))==nm['jars'][module]['sha256']
parent='src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/messaging/outbound/';helper_names=['OwnedOutboxDispatcher','OutboxDispatcher','OutboxEntry','JdbcOutboxRepository','OutboxJmsSender'];helpers={parent+n+'.java':sha(R/(parent+n+'.java')) for n in helper_names};assert all(nm['begin']['inputHashes'][n]==h for n,h in helpers.items())
dispatcher=tok((R/(parent+'OutboxDispatcher.java')).read_text())
assert tok('Connection connection = Objects.requireNonNull(connectionProvider.open(), "JDBC connection"); try {') in dispatcher
assert 'TemporaryInfrastructureException.attachSecondary(primary,secondary);' in dispatcher
assert 'try(Connectionconnection=transaction()){' in dispatcher
# No Connection value exists: transaction() exits before the try/cleanup and all claim/send/mark work.
assert tok('this.jitterPermille = Objects.requireNonNull(jitterPermille, "jitterPermille");') in tok((R/(parent+'JdbcOutboxRepository.java')).read_text())
index_path=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG23360-base59-named-proof-supplement-v1/current-normal-physical-index.json';assert sha(index_path)=='db6581ac589b42bdaa6e51ac101dac365d02a8fabab7d689eb5f12de29319723';index=load(index_path)
physical={n:v['sha256'] for n,v in index.items() if v['path'] in cfg['mainPaths']};assert physical==cfg['currentMainPhysical'] and len(physical)==1
metadata_path=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG23972-current-main-method-delta42-v1/class-method-inventory.json';rows=load(metadata_path);constructor_review=[]
for name in helper_names:
    row=next(v for v in rows if v['physicalKey']=='api:dev/codex/schubert/nk/api/messaging/outbound/'+name+'.class')
    assert row['sourceSha256']==helpers[row['sourcePath']] and not any(m['name']=='<clinit>' for m in row['structure']['methods'])
    if name=='OutboxJmsSender':assert next(m for m in row['structure']['methods'] if m['name']=='<init>')['codeLength']==5
    constructor_review.append(dict(path=row['sourcePath'],sourceSha256=row['sourceSha256'],physicalSha256=row['classSha256'],noOuterClassInitializer=True,reviewedUse='empty sender ctor' if name=='OutboxJmsSender' else ('fixed IntSupplier ctor only' if name=='JdbcOutboxRepository' else ('requireLeaseOwner static scalar only' if name=='OutboxEntry' else 'owned construction/dispatch failure path'))))
sdk=[]
for name,h in cfg['sdkDependencies'].items():
    p=Path(name);assert sha(p)==h and not any(x in p.name for x in ['postgresql','artemis-server'])
    with zipfile.ZipFile(p) as z:
        names=set(z.namelist());assert not names.intersection({'META-INF/services/java.sql.Driver','META-INF/services/javax.annotation.processing.Processor','META-INF/services/com.sun.source.util.Plugin'})
        mf=z.read('META-INF/MANIFEST.MF').decode() if 'META-INF/MANIFEST.MF' in names else '';assert not re.search(r'^Class-Path:',mf,re.M)
    sdk.append(dict(path=name,sha256=h,driverCompilerPluginOrExternalManifestClasspath=False))
O.parent.mkdir();value=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),inputHashes=pre['inputHashes'],compileManifestSha256=sha(RUNS/cfg['compileSlot']/'manifest.json'),staticManifestSha256=sha(RUNS/cfg['staticSlot']/'manifest.json'),normalManifestSha256=sha(normal),expectedTests=6,changedTestSources=1,changedLatchSites=2,innerFinallyReleaseBeforeExecutorClose=True,allOriginalTestOtherTokensAndOraclesPreserved=True,sourceForwardRecipeVerified=True,sourceNegativeChecks=negative,callbacks=callbacks,allSqlCallbacksNonReturning=True,noConnectionAcquiredBeforeFailure=True,heldAttachSecondaryUnreachable=True,repositoryMethodsAndJmsSendUnreachable=True,constructorReview=constructor_review,helperSourceHashes=helpers,pmdRawFindings=18,applicableStaticViolations=0,checkstyleFindings=0,processingErrors=0,suppressionAdded=False,staticClassifications=classifications,sdkReview=sdk,normalPositiveMainIndex={'path':str(index_path.relative_to(R)),'sha256':sha(index_path)},physical=physical,originalWholeTestClassSelection=True,noNewFixtureOrMethodExtraction=True,heldFourRuntimeOperationsAuthorized=False,actualBackendOperationsAuthorized=False,productTestsExecuted=0,newAcceptance=0,formalUpdated=False,effortRate=None,tool={'path':str(Path(__file__)),'sha256':sha(Path(__file__))})
O.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,expectedTests=6,targetPhysical=1,callbacks=9,pmdRaw=18,applicable=0,manifestSha256=sha(O))))
