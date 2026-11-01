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
NAME='dev/codex/schubert/nk/web/session/SessionStoreException'
AUTH='dev/codex/schubert/nk/api/security/AuthenticationInfrastructureException'
MAIN_UNITS={NAME:dict(module='web',name=NAME,sha256='93717ee948f88bd799a14cdad397c0d92e584711c32f571df8592be379033ed1'),AUTH:dict(module='api',name=AUTH,sha256='4b64f5d458370b67b3f5f156ffb879151eb69c30fbe9819660e70cc81e55a402')}
CLOSURES={NAME:[NAME],AUTH:[AUTH]}
METADATA=set()
METADATA_FLAGS={}
GENERATED_METADATA=set()
COUNTS={'SessionFailureGraphTest':1,'SessionJdbcGraph328Test':3,'AuthenticationFailureGraphTest':1,'AuthenticationJdbcGraph328Test':3}
PINS={'SessionFailureGraphTest':'3ab62c90af53ffb1e6fd9f01e650324bb16e201fd4eeecc7a5ba21f2127d7a10','SessionJdbcGraph328Test':'a946c07a2cd3b6c28d0ee244c42dd41de4706e03378418ec4462ae53c72551c0','AuthenticationFailureGraphTest':'d18eae10d916bfb12d1787a9eed3e1afa89ad4c6a3cffab9a51a4d306c97e0b3','AuthenticationJdbcGraph328Test':'88ea63184e86a97550683c94b545a17d530a38e924aac87733d89ce1e1ac2c70'}
ROOT=data.ROOT
TESTS={n:ROOT/('src/schubert-nk-'+m+'/src/test/java/dev/codex/schubert/nk/'+m+'/'+p+'/'+n+'.java') for n,m,p in [('SessionFailureGraphTest','web','session'),('SessionJdbcGraph328Test','web','session'),('AuthenticationFailureGraphTest','api','security'),('AuthenticationJdbcGraph328Test','api','security')]}
PUBLIC_READS={}
EXTRAS={}
FIXTURES={}
SESSION='PG17700-INDEPENDENT-SESSION-AUTH-GRAPH-ORIGINAL8'
REPORTER=ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
PLAN=data.BASE/'PG17700-session-auth-graph-review-v1'
def source_path(row):return 'src/schubert-nk-'+row['module']+'/src/main/java/'+row['name']+'.java'
if __name__=='__main__':
    invocation=capture(__file__);assert not PLAN.exists()
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA);current=normal['begin']['inputHashes']
    assert normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0
    old=data.read_checked(data.BASE/'PG17688-current2793-journal-deadline-registry-v1/manifest.json','2d5351879f409fee37b80492480fcb8a649cfd41f4a3e7a261dfabf4d1c57757')
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
    for row in MAIN_UNITS.values():
        text=(ROOT/source_path(row)).read_text()
        assert 'java.util.ArrayDeque<Throwable>' in text and 'java.util.IdentityHashMap<' in text
        assert not any(v in text for v in ['TemporaryInfrastructureException','WebStartupException','Connection','DriverManager','RootStartupContext','ServiceProcessResources'])
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12 and data.sha(REPORTER.read_bytes())=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    verify(invocation);PLAN.mkdir();data.write(PLAN/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewKind='FRESH_WHOLE_SOURCE_AND_ORIGINAL_TEST_REVIEW',reviewedMainInputs=reviewed,reviewedWholeTestInputs={str(p.relative_to(ROOT)):PINS[n] for n,p in TESTS.items()},currentNormalManifestSha256=COMPILE_SHA,originalWholeSuites=COUNTS,rootMemoryPortsOnly=False,memoryJournalQueryPortsOnly=False,syntheticOriginalOwnerPortsOnly=False,syntheticCompletionPublicationCallbacksInvoked=False,memoryRootScopeAndCleanupCompletionValuesOnly=False,declaredFakeExclusiveLockOnly=False,inMemoryCredentialBufferAndAclValuesOnly=False,testOwnSecureRandomFixtureBytesGenerated=False,publicFixedUuidFixtureOnly=False,syntheticScenarioPublisherCallbackInvoked=False,stubDescriptorContentHashNotVerified=False,realRuntimeCredentialOrKeyLoaded=False,publicDigestOnly=False,cryptoOrKeyOperationsInvoked=False,publicSourceReadHashes=PUBLIC_READS,testPublicSourceRead=False,syntheticPermitRecordConstructionOnly=False,nativeNamedReadNullGuardOnlyInvoked=False,independentModuleLocalThrowableGraphsOnly=True,junitTimeoutSeparateFrameworkWorkerOnly=True,actualPermitNamespaceLookups=0,actualRootOsAdmissionInvoked=False,reviewedOriginalHelperInputs=EXTRAS,syntheticRetirementCallbacksInvoked=False,declaredOwnedBenignChildCount=0,declaredOwnedMonitorWorkerCount=0,declaredOwnThreadCount=0,declaredOwnExecutorInstances=0,declaredOwnTaskCount=0,actualRootMemoryFixtureOnly=False,actualRootNativeObservations=0,actualGetentOrSystemctlInvoked=False,actualProcRead=False,priorProductResultsTransferred=False,productTestsExecutedByThisPlan=0,newAccepted=0,formalUpdated=False))
    run.SOURCE,run.COMPILE,run.COMPILE_SHA=SOURCE,COMPILE,COMPILE_SHA
    run.SLOT=run.host.W/'pg17700-session-auth-graph-eight-pt-v1';run.OUT=data.BASE/'PG17700-session-auth-graph-eight-pt-v1'
    run.HELPER=ROOT/'tools/quality/architecture/SessionAuthGraphEightCurrentJunitLauncher.java'
    run.NEW_TEST=TESTS['SessionFailureGraphTest'];run.TEST_ROOT=run.NEW_TEST.parent;run.TEST_SOURCE_OVERRIDES={n:p for n,p in TESTS.items() if n!='SessionFailureGraphTest'}
    run.EXTRA_TEST_SOURCES=(REPORTER,*(ROOT/p for p in EXTRAS));run.FIXTURES={};run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    run.step=environmental_step;run.main()
