"""Whole original terminal observation7; pure records and injected ResultSet getters, no DB."""
import re
import zipfile
from pg14296_web_target_mutation_whole_twenty_four_pt import environmental_step
import scoped_prometheus_host as run
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
COMPILE=run.host.W/'pg14216-typed-marker-guard-six-compile-v1'
COMPILE_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
PREFIX='dev/codex/schubert/nk/batch/repository/'
NAME=PREFIX+'MorningDatabaseSession'
MAIN_UNITS={PREFIX+n:dict(module='batch',name=PREFIX+n,sha256=h) for n,h in [('MorningDatabaseSession','27bda4446e8b0a112963704b95d530af2357d254f3f6bced1ce04284fb5e88e2'),('BackupStepRepository','8249ccf88e5620dc67d4f90a4206c9be05c810ea14693a6fa976ceb4e69e6e0d')]}
CLOSURES={NAME:[NAME+s for s in ['','$DatabaseObservation','$ExpiryObservation','$ExpiryBegins','$Bind','$BackupBegins','$RoleObservation','$Session','$BackupObservation','$Rows','$Schema','$CleanupHandoff','$Gate','$Operation','$Connect','$Access','$1']],PREFIX+'BackupStepRepository':[PREFIX+'BackupStepRepository'+s for s in ['','$Terminal']]}
METADATA={NAME+s for s in ['$Bind','$Rows','$CleanupHandoff','$Gate','$Operation','$Connect']}
METADATA_FLAGS={n:(1537 if n.endswith(('$CleanupHandoff','$Operation')) else 1536) for n in METADATA}
GENERATED_METADATA=set()
COUNTS={'MorningExpiryObservationInvariantTest':4,'BackupTerminalObservationTest':3}
PINS={'MorningExpiryObservationInvariantTest':'7daa2c142d09b03d16033551d7601352b51540ceadcba5eaf16d0455d7ee912f','BackupTerminalObservationTest':'dc454eff471dd12976b0fd0acc6df8eb9c6edcbfcfbe71a9ace0087461b30311'}
ROOT=data.ROOT
TESTS={n:ROOT/('src/schubert-nk-batch/src/test/java/'+PREFIX+n+'.java') for n in COUNTS}
EXTRAS={'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/ExpiryReceiptFixture.java':'abf309d8c2126bbad37c7c2024c95aa6a59965f74053f306fd7ed337c7747375'}
FIXTURES={}
SESSION='PG17180-MORNING-TERMINAL-OBSERVATION-ORIGINAL7'
REPORTER=ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
PLAN=data.BASE/'PG17179-morning-terminal-observation-review-v1'
def source_path(row):return 'src/schubert-nk-'+row['module']+'/src/main/java/'+row['name']+'.java'
if __name__=='__main__':
    invocation=capture(__file__);assert not PLAN.exists()
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA);current=normal['begin']['inputHashes']
    assert normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0
    old=data.read_checked(data.BASE/'PG17166-current2609-morning-launch-owner-registry-v1/manifest.json','597a383e5895c727c3bd3b1a014eeb4fd5bc03db4d9c21a2066b2cc95ee79253')
    assert old['source']==SOURCE and not set(MAIN_UNITS)&old['fullSourceUnits'].keys()
    for name,path in TESTS.items():
        text=path.read_text();relative=str(path.relative_to(ROOT))
        assert data.sha(path.read_bytes())==PINS[name]==current[relative]
        assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+\w+\s*\(',text))==COUNTS[name]
        assert 'dev.codex.schubert.nk.batch.repository.'+name not in old['suiteNames']
        assert not any(v in text for v in ['@Before','@After','@TempDir','DriverManager','ProcessBuilder','TemporaryInfrastructureException','WebStartupException','RootFailedStartRecovery','LinuxDirectoryCalls','ApiProcessLifetime','ServiceProcessResources','.install(','.retainUnknown(','Thread.sleep','Runtime.getRuntime','addShutdownHook','removeShutdownHook','RootStartupContext.create(','new RootStartupContext.NativeIo'])
    for path,pin in EXTRAS.items():assert data.sha((ROOT/path).read_bytes())==current[path]==pin
    reviewed={}
    for name,row in MAIN_UNITS.items():
        path=source_path(row);assert row['sha256']==current[path]==data.sha((ROOT/path).read_bytes());reviewed[path]=row['sha256']
        with zipfile.ZipFile(normal['jars'][row['module']]['path']) as jar:assert {n[:-6] for n in jar.namelist() if n==name+'.class' or n.startswith(name+'$') and n.endswith('.class')}==set(CLOSURES[name])
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12 and data.sha(REPORTER.read_bytes())=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    verify(invocation);PLAN.mkdir();data.write(PLAN/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewKind='FRESH_TARGET_METHOD_AND_WHOLE_ORIGINAL_TEST_REVIEW_ALL_SOURCE_BYTES_BOUND_NOT_WHOLE_PG_ACCEPTANCE',reviewedMainInputs=reviewed,reviewedMethodScope={'MorningDatabaseSession':['BackupObservation','ExpiryBegins','ExpiryObservation'],'BackupStepRepository':['Terminal','readTerminal','present','require']},wholeMorningDatabaseSessionRuntimeReviewComplete=False,reviewedWholeTestInputs={str(p.relative_to(ROOT)):PINS[n] for n,p in TESTS.items()},currentNormalManifestSha256=COMPILE_SHA,originalWholeSuites=COUNTS,rootMemoryPortsOnly=False,memoryJournalQueryPortsOnly=False,syntheticOriginalOwnerPortsOnly=False,syntheticCompletionPublicationCallbacksInvoked=False,memoryRootScopeAndCleanupCompletionValuesOnly=False,declaredFakeExclusiveLockOnly=False,memoryTerminalObservationValuesOnly=True,syntheticResultSetGettersOnly=True,publicDigestOnly=False,cryptoOrKeyOperationsInvoked=False,reviewedOriginalHelperInputs=EXTRAS,syntheticRetirementCallbacksInvoked=False,declaredOwnedBenignChildCount=0,declaredOwnedMonitorWorkerCount=0,declaredOwnThreadCount=0,declaredOwnExecutorInstances=0,declaredOwnTaskCount=0,actualRootMemoryFixtureOnly=False,actualRootNativeObservations=0,actualGetentOrSystemctlInvoked=False,actualProcRead=False,priorProductResultsTransferred=False,productTestsExecutedByThisPlan=0,newAccepted=0,formalUpdated=False))
    run.SOURCE,run.COMPILE,run.COMPILE_SHA=SOURCE,COMPILE,COMPILE_SHA
    run.SLOT=run.host.W/'pg17180-morning-terminal-observation-seven-pt-v1';run.OUT=data.BASE/'PG17180-morning-terminal-observation-seven-pt-v1'
    run.HELPER=ROOT/'tools/quality/architecture/MorningTerminalObservationSevenCurrentJunitLauncher.java'
    run.NEW_TEST=TESTS['MorningExpiryObservationInvariantTest'];run.TEST_ROOT=run.NEW_TEST.parent;run.TEST_SOURCE_OVERRIDES={}
    run.EXTRA_TEST_SOURCES=(REPORTER,*(ROOT/p for p in EXTRAS));run.FIXTURES={};run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    run.step=environmental_step;run.main()
