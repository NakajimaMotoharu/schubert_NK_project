"""Whole original retained audit14/Caddy floor1 values; no SQL/native/root or actual clock."""
import re
import zipfile
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import scoped_prometheus_host as run
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
PREFIX='dev/codex/schubert/nk/batch/file/'
NAME=PREFIX+'CleanupExpiryExecution'
OTHER=PREFIX+'MorningStartupLaunchOwner'
MAIN_UNITS={NAME:dict(module='batch',name=NAME,sha256='f7100ed36f815cb45f44e6ab9d829d183d359f6aa437aed6c8203d27863b8c3b'),OTHER:dict(module='batch',name=OTHER,sha256='caca5ef9c6f8ab5e5084bf0ee363871b5e61fce4f023fd3daf9ca484faa0d99a')}
CLOSURES={NAME:[NAME,NAME+'$ExpiryWork',NAME+'$1'],OTHER:[OTHER,*(OTHER+'$'+s for s in ['Stop','Launch','CompletionProgress','CompletionRetirement','Completion','Started','ApiRetained','CompletionPhase'])]}
METADATA={NAME+'$ExpiryWork',*(OTHER+'$'+s for s in ['Stop','Launch','CompletionRetirement','Completion','ApiRetained'])}
METADATA_FLAGS={n:1536 for n in METADATA}
GENERATED_METADATA=set()
COUNTS={'RetainedExpiryAuditTest':14,'CaddyParentRemainingBudgetTest':1}
PINS={'RetainedExpiryAuditTest':'940314bd129138fc114510684e109c249f4d0eb4359e4f1c708e06ded3db053d','CaddyParentRemainingBudgetTest':'4597cedb3006c031d335fd76a1001c80b23b74fb904ad475d72aad1980fcf645'}
ROOT=data.ROOT
TESTS={n:ROOT/('src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/'+n+'.java') for n in COUNTS}
PUBLIC_READS={}
EXTRAS={}
FIXTURES={}
SESSION='PG17580-RETAINED-AUDIT-CADDY-ORIGINAL15'
REPORTER=ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
PLAN=data.BASE/'PG17579-retained-audit-caddy-review-v1'
def source_path(row):return 'src/schubert-nk-'+row['module']+'/src/main/java/'+row['name']+'.java'
if __name__=='__main__':
    invocation=capture(__file__);assert not PLAN.exists()
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA);current=normal['begin']['inputHashes']
    assert normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0
    old=data.read_checked(data.BASE/'PG17548-current2747-api-default-bind-registry-v1/manifest.json','0b583d1976bd9dfb6ea7a2aaa245aed45efc91efcecc679103904e6424464426')
    assert old['source']==SOURCE and set(MAIN_UNITS)<=old['fullSourceUnits'].keys()
    for name,path in TESTS.items():
        text=path.read_text();relative=str(path.relative_to(ROOT))
        assert data.sha(path.read_bytes())==PINS[name]==current[relative]
        assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+\w+\s*\(',text))==COUNTS[name]
        assert next(v.removeprefix('package ').removesuffix(';') for v in text.splitlines() if v.startswith('package '))+'.'+name not in old['suiteNames']
        assert not any(v in text for v in ['@Before','@After','@TempDir','DriverManager','ProcessBuilder','TemporaryInfrastructureException','WebStartupException','RootFailedStartRecovery','LinuxDirectoryCalls','ApiProcessLifetime','ServiceProcessResources','.install(','.retainUnknown(','Thread.sleep','Runtime.getRuntime','addShutdownHook','removeShutdownHook','RootStartupContext.create(','new RootStartupContext.NativeIo'])
    for path,pin in PUBLIC_READS.items():assert data.sha((ROOT/path).read_bytes())==data.sha((COMPILE/'snapshot'/path).read_bytes())==current[path]==pin
    for path,pin in EXTRAS.items():assert data.sha((ROOT/path).read_bytes())==current[path]==pin
    reviewed={}
    for name,row in MAIN_UNITS.items():
        path=source_path(row);assert row['sha256']==current[path]==data.sha((ROOT/path).read_bytes());reviewed[path]=row['sha256']
        with zipfile.ZipFile(normal['jars'][row['module']]['path']) as jar:assert {n[:-6] for n in jar.namelist() if n==name+'.class' or n.startswith(name+'$') and n.endswith('.class')}==set(CLOSURES[name])
    for ref in [('PG17479-expiry-owner-review-v1','a6c95a76060f52beed8da39c41e0759dc5cc3d78c06e0008272a1c0d97d9edd1'),('PG16617-morning-static-review-equivalence-v1','b7589a46ea931fd4ad14e553453d8501eb8d5a790ececcfe31f74761bd124d15')]:
        previous=data.read_checked(data.BASE/ref[0]/'manifest.json',ref[1]);assert previous['actualExit']==0 and previous['source']==SOURCE;verify(previous['invocation'])
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12 and data.sha(REPORTER.read_bytes())=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    verify(invocation);PLAN.mkdir();data.write(PLAN/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewKind='PRIOR_WHOLE_MAIN_STATIC_REVIEW_REUSED_NEW_WHOLE_TEST15_AND_CALLED_STATIC_BODY_REVIEW',priorWholeMainReviewReferences=[['PG17479-expiry-owner-review-v1','a6c95a76060f52beed8da39c41e0759dc5cc3d78c06e0008272a1c0d97d9edd1'],['PG16617-morning-static-review-equivalence-v1','b7589a46ea931fd4ad14e553453d8501eb8d5a790ececcfe31f74761bd124d15']],supplementaryScopeOnly=True,reviewedMainInputs=reviewed,reviewedWholeTestInputs={str(p.relative_to(ROOT)):PINS[n] for n,p in TESTS.items()},currentNormalManifestSha256=COMPILE_SHA,originalWholeSuites=COUNTS,rootMemoryPortsOnly=False,memoryJournalQueryPortsOnly=False,syntheticOriginalOwnerPortsOnly=False,syntheticCompletionPublicationCallbacksInvoked=False,memoryRootScopeAndCleanupCompletionValuesOnly=False,declaredFakeExclusiveLockOnly=False,inMemoryCredentialBufferAndAclValuesOnly=False,testOwnSecureRandomFixtureBytesGenerated=False,publicFixedUuidFixtureOnly=False,syntheticScenarioPublisherCallbackInvoked=False,stubDescriptorContentHashNotVerified=False,realRuntimeCredentialOrKeyLoaded=False,publicDigestOnly=False,cryptoOrKeyOperationsInvoked=False,publicSourceReadHashes=PUBLIC_READS,testPublicSourceRead=False,reviewedOriginalHelperInputs=EXTRAS,syntheticRetirementCallbacksInvoked=False,declaredOwnedBenignChildCount=0,declaredOwnedMonitorWorkerCount=0,declaredOwnThreadCount=0,declaredOwnExecutorInstances=0,declaredOwnTaskCount=0,actualRootMemoryFixtureOnly=False,actualRootNativeObservations=0,actualGetentOrSystemctlInvoked=False,actualProcRead=False,priorProductResultsTransferred=False,productTestsExecutedByThisPlan=0,newAccepted=0,formalUpdated=False))
    run.SOURCE,run.COMPILE,run.COMPILE_SHA=SOURCE,COMPILE,COMPILE_SHA
    run.SLOT=run.host.W/'pg17580-retained-audit-caddy-fifteen-pt-v1';run.OUT=data.BASE/'PG17580-retained-audit-caddy-fifteen-pt-v1'
    run.HELPER=ROOT/'tools/quality/architecture/RetainedAuditCaddyFifteenCurrentJunitLauncher.java'
    run.NEW_TEST=TESTS['RetainedExpiryAuditTest'];run.TEST_ROOT=run.NEW_TEST.parent;run.TEST_SOURCE_OVERRIDES={}
    run.EXTRA_TEST_SOURCES=(REPORTER,*(ROOT/p for p in EXTRAS));run.FIXTURES={};run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    run.step=environmental_step;run.main()
