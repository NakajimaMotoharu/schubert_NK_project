"""Original independent Session/Auth Throwable graphs; no held classifier or actual JDBC operation."""
import re
import zipfile
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import scoped_prometheus_host as run
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
NAME='dev/codex/schubert/nk/web/receipt/ReceiptReferenceRepository'
ERROR='dev/codex/schubert/nk/web/receipt/ReceiptReferenceException'
MAIN_UNITS={NAME:dict(module='web',name=NAME,sha256='91ca27ecb2aea560cd08b26c0ef605b2bbbac756afb673722eef816a1ddfb2c4'),ERROR:dict(module='web',name=ERROR,sha256='da9b11facf9c66b91e19f8a5dce97509cc759c9d88aab63704419cc3e9777cd9')}
CLOSURES={NAME:[NAME,NAME+'$Work'],ERROR:[ERROR]}
METADATA={NAME+'$Work'}
METADATA_FLAGS={NAME+'$Work':1536}
GENERATED_METADATA=set()
COUNTS={'ReceiptFailureGraph329Test':3}
PINS={'ReceiptFailureGraph329Test':'f5a92b64eb2f5b560963454360422666731cc2fcc995ad8a5b35d3c320fdd466'}
ROOT=data.ROOT
TESTS={'ReceiptFailureGraph329Test':ROOT/'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/receipt/ReceiptFailureGraph329Test.java'}
PUBLIC_READS={'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/receipt/ReceiptReference.java':'b8dff7e53fd4b8646817eb6673a57479d3746a37d01585c3e35c2eee749ff829','src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/session/SessionStoreException.java':'93717ee948f88bd799a14cdad397c0d92e584711c32f571df8592be379033ed1'}
EXTRAS={}
FIXTURES={}
SESSION='PG17760-RECEIPT-OWNED-GRAPH-ORIGINAL3'
REPORTER=ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
PLAN=data.BASE/'PG17760-receipt-owned-graph-review-v1'
def source_path(row):return 'src/schubert-nk-'+row['module']+'/src/main/java/'+row['name']+'.java'
if __name__=='__main__':
    invocation=capture(__file__);assert not PLAN.exists()
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA);current=normal['begin']['inputHashes']
    assert normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0
    old=data.read_checked(data.BASE/'PG17748-current2807-auth-borrowed-boundary-registry-v1/manifest.json','d3209b354ef0d91ca7f7877a511f2744591d7fff4605f5885a637107287c11f5')
    assert old['source']==SOURCE and not set(MAIN_UNITS)&old['fullSourceUnits'].keys()
    for name,path in TESTS.items():
        text=path.read_text();relative=str(path.relative_to(ROOT))
        assert data.sha(path.read_bytes())==PINS[name]==current[relative]
        assert text.count('@Test')==len(re.findall(r'@Test(?:\s*@Timeout\([^)]*\))?\s+void\s+\w+\s*\(',text))==COUNTS[name]
        assert next(v.removeprefix('package ').removesuffix(';') for v in text.splitlines() if v.startswith('package '))+'.'+name not in old['suiteNames']
        assert not any(v in text for v in ['@Before','@After','@TempDir','DriverManager','ProcessBuilder','TemporaryInfrastructureException','WebStartupException','RootFailedStartRecovery','LinuxDirectoryCalls','ApiProcessLifetime','ServiceProcessResources','.install(','.retainUnknown(','Thread.sleep','Runtime.getRuntime','addShutdownHook','removeShutdownHook','RootStartupContext.create(','new RootStartupContext.NativeIo'])
    for path,pin in PUBLIC_READS.items():assert data.sha((ROOT/path).read_bytes())==data.sha((COMPILE/'snapshot'/path).read_bytes())==current[path]==pin
    for path,pin in EXTRAS.items():assert data.sha((ROOT/path).read_bytes())==current[path]==pin
    reviewed={}
    for name,row in MAIN_UNITS.items():
        path=source_path(row);assert row['sha256']==current[path]==data.sha((ROOT/path).read_bytes());reviewed[path]=row['sha256']
        with zipfile.ZipFile(normal['jars'][row['module']]['path']) as jar:assert {n[:-6] for n in jar.namelist() if n==name+'.class' or n.startswith(name+'$') and n.endswith('.class')}==set(CLOSURES[name])
    text=(ROOT/source_path(MAIN_UNITS[NAME])).read_text()
    assert 'SessionStoreException.preserveFatal' in text and 'primary.addSuppressed(new ReceiptReferenceException())' in text
    assert not any(v in text for v in ['WebStartupException','TemporaryInfrastructureException','DriverManager','RootStartupContext','ServiceProcessResources'])
    test=TESTS['ReceiptFailureGraph329Test'].read_text()
    assert 'assertEquals(0, fixture.commits' in test and 'assertEquals(1, fixture.connectionCloses' in test
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12 and data.sha(REPORTER.read_bytes())=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    verify(invocation);PLAN.mkdir();data.write(PLAN/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewKind='FRESH_WHOLE_SOURCE_AND_ORIGINAL_TEST_REVIEW',reviewedMainInputs=reviewed,reviewedWholeTestInputs={str(p.relative_to(ROOT)):PINS[n] for n,p in TESTS.items()},currentNormalManifestSha256=COMPILE_SHA,originalWholeSuites=COUNTS,rootMemoryPortsOnly=False,memoryJournalQueryPortsOnly=False,syntheticOriginalOwnerPortsOnly=False,syntheticCompletionPublicationCallbacksInvoked=False,memoryRootScopeAndCleanupCompletionValuesOnly=False,declaredFakeExclusiveLockOnly=False,inMemoryCredentialBufferAndAclValuesOnly=False,testOwnSecureRandomFixtureBytesGenerated=False,publicFixedUuidFixtureOnly=False,syntheticScenarioPublisherCallbackInvoked=False,stubDescriptorContentHashNotVerified=False,realRuntimeCredentialOrKeyLoaded=False,publicDigestOnly=False,cryptoOrKeyOperationsInvoked=False,publicSourceReadHashes=PUBLIC_READS,testPublicSourceRead=False,syntheticPermitRecordConstructionOnly=False,nativeNamedReadNullGuardOnlyInvoked=False,independentModuleLocalThrowableGraphsOnly=False,syntheticOwnedReceiptJdbcFaultPortsOnly=True,junitTimeoutSeparateFrameworkWorkerOnly=True,actualPermitNamespaceLookups=0,actualRootOsAdmissionInvoked=False,reviewedOriginalHelperInputs=EXTRAS,syntheticRetirementCallbacksInvoked=False,declaredOwnedBenignChildCount=0,declaredOwnedMonitorWorkerCount=0,declaredOwnThreadCount=0,declaredOwnExecutorInstances=0,declaredOwnTaskCount=0,actualRootMemoryFixtureOnly=False,actualRootNativeObservations=0,actualGetentOrSystemctlInvoked=False,actualProcRead=False,priorProductResultsTransferred=False,productTestsExecutedByThisPlan=0,newAccepted=0,formalUpdated=False))
    run.SOURCE,run.COMPILE,run.COMPILE_SHA=SOURCE,COMPILE,COMPILE_SHA
    run.SLOT=run.host.W/'pg17760-receipt-owned-graph-three-pt-v1';run.OUT=data.BASE/'PG17760-receipt-owned-graph-three-pt-v1'
    run.HELPER=ROOT/'tools/quality/architecture/ReceiptOwnedGraphThreeCurrentJunitLauncher.java'
    run.NEW_TEST=TESTS['ReceiptFailureGraph329Test'];run.TEST_ROOT=run.NEW_TEST.parent;run.TEST_SOURCE_OVERRIDES={}
    run.EXTRA_TEST_SOURCES=(REPORTER,*(ROOT/p for p in EXTRAS));run.FIXTURES={};run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    run.step=environmental_step;run.main()
