"""Original whole no-prior Broker eight; only reviewed injected memory ports and two public golden resources."""
import re
import zipfile
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import scoped_prometheus_host as run
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
PREFIX='dev/codex/schubert/nk/batch/platform/'
NAME=PREFIX+'MorningStopPass'
MAIN_UNITS={n:dict(module='batch',name=n,sha256=h) for n,h in [(NAME,'42c1f37aa5f8c40d5c1b1f8900028eb54022eae678f1850307e4156e854c8e88'),('dev/codex/schubert/nk/batch/file/MorningGateEvidence','c5c0295c1c8da89bad0890cad123366462e46941e6902f987dc17b77bc515d8a')]}
CLOSURES={NAME:[NAME+s for s in ['','$1','$1$1','$2','$Attempt','$Gate','$Stop','$Terminals']],'dev/codex/schubert/nk/batch/file/MorningGateEvidence':['dev/codex/schubert/nk/batch/file/MorningGateEvidence']}
METADATA={NAME+s for s in ['$Attempt','$Gate','$Stop','$Terminals']}
METADATA_FLAGS={n:1536 for n in METADATA}
GENERATED_METADATA=set()
COUNTS={'MorningStopPassTest':10,'PostgresObservationRowsTest':1}
PINS={'MorningStopPassTest':'49468471989ff6f0bf59c1e63145a8e6f82ca79bb02e50a6e60919d96bfe052f','PostgresObservationRowsTest':'8fa5e740df60f53477948233afc1a75b5e999bc6f92f87d99798d5998f63a119'}
ROOT=data.ROOT
TESTS={n:ROOT/('src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/'+('file/' if n=='PostgresObservationRowsTest' else 'platform/')+n+'.java') for n in COUNTS}
EXTRAS={'src/schubert-nk-batch/src/test/java/'+PREFIX+'RootStartupContextTest.java':'f3de04b3c6043aed5e6871bc1de15b8108da8cf7adacad206d0a8a0b88a71811'}
FIXTURES={}
SESSION='PG17104-STOP-PASS-POSTGRES-ROWS-ORIGINAL11'
REPORTER=ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
PLAN=data.BASE/'PG17103-stop-pass-postgres-rows-review-v1'
def source_path(row):return 'src/schubert-nk-'+row['module']+'/src/main/java/'+row['name']+'.java'
if __name__=='__main__':
    invocation=capture(__file__);assert not PLAN.exists()
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA);current=normal['begin']['inputHashes']
    assert normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0
    old=data.read_checked(data.BASE/'PG17094-current2575-broker-cycle-query-registry-v1/manifest.json','77c898f3394948f03a994af4724920366b50b921b7f6e99096d6be2957e7b172')
    assert old['source']==SOURCE and set(MAIN_UNITS)-old['fullSourceUnits'].keys()=={NAME}
    for name,path in TESTS.items():
        text=path.read_text();relative=str(path.relative_to(ROOT))
        assert data.sha(path.read_bytes())==PINS[name]==current[relative]
        assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+\w+\s*\(',text))==COUNTS[name]
        assert relative.split('/src/test/java/',1)[1][:-5].replace('/','.') not in old['suiteNames']
        assert not any(v in text for v in ['@Before','@After','@TempDir','DriverManager','ProcessBuilder','TemporaryInfrastructureException','WebStartupException','RootFailedStartRecovery','LinuxDirectoryCalls','ApiProcessLifetime','ServiceProcessResources','.install(','.retainUnknown(','Thread.sleep','Runtime.getRuntime','addShutdownHook','removeShutdownHook','RootStartupContext.create(','new RootStartupContext.NativeIo'])
    for path,pin in {**EXTRAS,**FIXTURES}.items():assert data.sha((ROOT/path).read_bytes())==current[path]==pin
    reviewed={}
    for name,row in MAIN_UNITS.items():
        path=source_path(row);assert row['sha256']==current[path]==data.sha((ROOT/path).read_bytes());reviewed[path]=row['sha256']
        with zipfile.ZipFile(normal['jars'][row['module']]['path']) as jar:assert {n[:-6] for n in jar.namelist() if n==name+'.class' or n.startswith(name+'$') and n.endswith('.class')}==set(CLOSURES[name])
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12 and data.sha(REPORTER.read_bytes())=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    verify(invocation);PLAN.mkdir();data.write(PLAN/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewKind='FRESH_WHOLE_SOURCE_AND_ORIGINAL_TEST_REVIEW',reviewedMainInputs=reviewed,reviewedWholeTestInputs={str(p.relative_to(ROOT)):PINS[n] for n,p in TESTS.items()},currentNormalManifestSha256=COMPILE_SHA,originalWholeSuites=COUNTS,rootMemoryPortsOnly=True,memoryJournalQueryPortsOnly=False,pureStopPassCallbacksAndPostgresRecordFormatterOnly=True,publicDigestOnly=False,cryptoOrKeyOperationsInvoked=False,reviewedOriginalHelperInputs=EXTRAS,syntheticRetirementCallbacksInvoked=False,declaredOwnedBenignChildCount=0,declaredOwnedMonitorWorkerCount=0,actualRootMemoryFixtureOnly=True,actualRootNativeObservations=0,actualGetentOrSystemctlInvoked=False,actualProcRead=False,priorProductResultsTransferred=False,declaredOwnThreadCount=2,declaredOwnExecutorInstances=2,declaredOwnTaskCount=2,ownCurrentThreadInterruptFlagModifiedAndFinallyCleared=True,publicRandomUuidValueOnly=False,testPublicGoldenResourcesRead=False,productTestsExecutedByThisPlan=0,newAccepted=0,formalUpdated=False))
    run.SOURCE,run.COMPILE,run.COMPILE_SHA=SOURCE,COMPILE,COMPILE_SHA
    run.SLOT=run.host.W/'pg17104-stop-pass-postgres-rows-eleven-pt-v1';run.OUT=data.BASE/'PG17104-stop-pass-postgres-rows-eleven-pt-v1'
    run.HELPER=ROOT/'tools/quality/architecture/StopPassPostgresRowsElevenCurrentJunitLauncher.java'
    run.NEW_TEST=TESTS['MorningStopPassTest'];run.TEST_ROOT=run.NEW_TEST.parent;run.TEST_SOURCE_OVERRIDES={n:p for n,p in TESTS.items() if n=='PostgresObservationRowsTest'}
    run.EXTRA_TEST_SOURCES=(REPORTER,*(ROOT/p for p in EXTRAS));run.FIXTURES=FIXTURES;run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    run.step=environmental_step;run.main()
