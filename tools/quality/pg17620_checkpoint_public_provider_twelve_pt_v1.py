"""Whole original public provider/checkpoint12; fake agent/export and empty reserved profile, no native authority."""
import re
import zipfile
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import scoped_prometheus_host as run
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
PREFIX='dev/codex/schubert/nk/bootstrap/'
NAME=PREFIX+'FixedNativeCoverageCheckpoint'
MAIN_UNITS={NAME:dict(module='bootstrap',name=NAME,sha256='95d70220aaa00265151d92ec1c4d4e5e7e220ed4508668461ce0b497b988e86d')}
CLOSURES={NAME:[NAME,*(NAME+'$'+s for s in ['Agent','Export','Point','PublicAgent','PublicAgent$Classes','PublicAgent$Sources','PublicAgent$Invocation'])]}
METADATA={NAME+'$'+s for s in ['Agent','Export','PublicAgent$Classes','PublicAgent$Sources','PublicAgent$Invocation']}
METADATA_FLAGS={n:1536 for n in METADATA}
GENERATED_METADATA=set()
COUNTS={'FixedNativeCoverageCheckpointTest':12}
PINS={'FixedNativeCoverageCheckpointTest':'40d28e8f5c637ed3bade554aa703d828bbd279cb22aa43c2a9edcc6228183264'}
ROOT=data.ROOT
TESTS={'FixedNativeCoverageCheckpointTest':ROOT/'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/bootstrap/FixedNativeCoverageCheckpointTest.java'}
PUBLIC_READS={}
EXTRAS={}
FIXTURES={}
SESSION='PG17620-CHECKPOINT-PUBLIC-PROVIDER-ORIGINAL12'
REPORTER=ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
PLAN=data.BASE/'PG17619-checkpoint-public-provider-review-v1'
def source_path(row):return 'src/schubert-nk-'+row['module']+'/src/main/java/'+row['name']+'.java'
if __name__=='__main__':
    invocation=capture(__file__);assert not PLAN.exists()
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA);current=normal['begin']['inputHashes']
    assert normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0
    old=data.read_checked(data.BASE/'PG17588-current2762-retained-audit-caddy-registry-v1/manifest.json','c45a5c686a95d6a67c297fed02b56832446a7558d89ced8acc1ace58b48031dd')
    assert old['source']==SOURCE and not set(MAIN_UNITS)&old['fullSourceUnits'].keys()
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
    text=TESTS['FixedNativeCoverageCheckpointTest'].read_text()
    assert 'FixedNativeCoveragePrivateFile' not in text and 'NativeCoveragePrivateFile' not in text and 'System.setProperty' not in text and 'Class.forName' not in text
    assert 'agentRefused(FixedNativeCoverageCheckpoint.PublicAgent::new);' in text and 'new PublicFixture()' in text and 'newFixedThreadPool(4)' in text
    assert str(run.AGENT).startswith(str(run.host.TC)+'/') and not str(run.AGENT).startswith('/opt/pgpt-tools-pg390/')
    assert 'if (profile.isEmpty()) return Optional.empty();' in (ROOT/source_path(MAIN_UNITS[NAME])).read_text()
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12 and data.sha(REPORTER.read_bytes())=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    verify(invocation);PLAN.mkdir();data.write(PLAN/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewKind='FRESH_WHOLE_SOURCE_AND_ORIGINAL_TEST_REVIEW',reviewedMainInputs=reviewed,reviewedWholeTestInputs={str(p.relative_to(ROOT)):PINS[n] for n,p in TESTS.items()},currentNormalManifestSha256=COMPILE_SHA,originalWholeSuites=COUNTS,rootMemoryPortsOnly=False,memoryJournalQueryPortsOnly=False,syntheticOriginalOwnerPortsOnly=False,syntheticCompletionPublicationCallbacksInvoked=False,memoryRootScopeAndCleanupCompletionValuesOnly=False,declaredFakeExclusiveLockOnly=False,inMemoryCredentialBufferAndAclValuesOnly=False,testOwnSecureRandomFixtureBytesGenerated=False,publicFixedUuidFixtureOnly=False,syntheticScenarioPublisherCallbackInvoked=False,stubDescriptorContentHashNotVerified=False,realRuntimeCredentialOrKeyLoaded=False,publicDigestOnly=False,cryptoOrKeyOperationsInvoked=False,publicSourceReadHashes=PUBLIC_READS,testPublicSourceRead=False,testOwnPublicClassResourceRead=True,publicOnlyReflectionInvoked=True,declaredOwnMetadataClassDefinitions=4,actualNativeExporterOperation=False,reviewedOriginalHelperInputs=EXTRAS,syntheticRetirementCallbacksInvoked=False,declaredOwnedBenignChildCount=0,declaredOwnedMonitorWorkerCount=0,declaredOwnThreadCount=None,declaredOwnExecutorInstances=1,declaredOwnTaskCount=32,actualRootMemoryFixtureOnly=False,actualRootNativeObservations=0,actualGetentOrSystemctlInvoked=False,actualProcRead=False,priorProductResultsTransferred=False,productTestsExecutedByThisPlan=0,newAccepted=0,formalUpdated=False))
    run.SOURCE,run.COMPILE,run.COMPILE_SHA=SOURCE,COMPILE,COMPILE_SHA
    run.SLOT=run.host.W/'pg17620-checkpoint-public-provider-twelve-pt-v1';run.OUT=data.BASE/'PG17620-checkpoint-public-provider-twelve-pt-v1'
    run.HELPER=ROOT/'tools/quality/architecture/CheckpointPublicProviderTwelveCurrentJunitLauncher.java'
    run.NEW_TEST=TESTS['FixedNativeCoverageCheckpointTest'];run.TEST_ROOT=run.NEW_TEST.parent;run.TEST_SOURCE_OVERRIDES={}
    run.EXTRA_TEST_SOURCES=(REPORTER,*(ROOT/p for p in EXTRAS));run.FIXTURES={};run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    run.step=environmental_step;run.main()
