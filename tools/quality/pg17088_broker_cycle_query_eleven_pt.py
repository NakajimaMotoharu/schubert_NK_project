"""Three complete original Root memory-fixture suites; no native provider or external resources."""
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
NAME=PREFIX+'InspectorUnitProbe'
MAIN_UNITS={PREFIX+n:dict(module='batch',name=PREFIX+n,sha256=h) for n,h in [('InspectorUnitProbe','cfd6a67fba5f487f3e3f5195ca9a308c1c9ad447a295fe22b8ed230ae8cac9a0'),('MorningBrokerUnitCycle','5c69b77ddb52446e8fc833222d8402da87e23ae589b8c0cdc90c6a8061c649c5')]}
CLOSURES={NAME:[NAME+s for s in ['','$NativeReader','$NativeReader$Start','$Reader','$SafeStream','$QueryProcess']],PREFIX+'MorningBrokerUnitCycle':[PREFIX+'MorningBrokerUnitCycle'+s for s in ['','$Live','$Baseline','$Readiness','$1','$Retain','$Observation','$Start','$Projection','$ParentProof']]}
METADATA={NAME+s for s in ['$Reader','$NativeReader$Start']}|{PREFIX+'MorningBrokerUnitCycle'+s for s in ['$Readiness','$Retain','$Start','$Projection','$ParentProof']}
METADATA_FLAGS={n:1537 if n.endswith(('$Readiness','$ParentProof')) else 1536 for n in METADATA}
GENERATED_METADATA=set()
COUNTS={'MorningBrokerUnitCycleTest':6,'BrokerJournalQueryTest':5}
PINS={'MorningBrokerUnitCycleTest':'298e637df1d718f5a04aff184bdc26cc21b9038b314b318e2fda8658d5eb3eb0','BrokerJournalQueryTest':'935ce8afed0d16ad9b8617c647ceb921eb0d28edc9438cf7e2ac5f58eaa9f745'}
ROOT=data.ROOT
TESTS={n:ROOT/('src/schubert-nk-batch/src/test/java/'+PREFIX+n+'.java') for n in COUNTS}
EXTRAS={'src/schubert-nk-batch/src/test/java/'+PREFIX+n+'.java':h for n,h in [('BrokerJournalEvidenceTest','73ec7a8bca1a6540dec83520b7072b56fd7c988e55d9d1a86afb67b0a9125a02'),('InspectorUnitProbeFixture','75b62aea8f3e4fbc558ec24698c7ff7d1faf4f477f34addb17e5e58f1283da2b'),('InspectorUnitSnapshotTest','edf0ce67d649d340e2e61907cc8228cd9c44fe08a21a9f011d81cdcbef4d1a63')]}
FIXTURES={}
SESSION='PG17088-BROKER-CYCLE-QUERY-ORIGINAL11'
REPORTER=ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
PLAN=data.BASE/'PG17087-broker-cycle-query-review-v1'
def source_path(row):return 'src/schubert-nk-'+row['module']+'/src/main/java/'+row['name']+'.java'
if __name__=='__main__':
    invocation=capture(__file__);assert not PLAN.exists()
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA);current=normal['begin']['inputHashes']
    assert normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0
    old=data.read_checked(data.BASE/'PG17076-current2564-morning-gate-evidence-registry-v1/manifest.json','b2d956a16015cad96c7ee106ace35071b4ca5d37b54c72a08777f0896adda540')
    assert old['source']==SOURCE and set(MAIN_UNITS)<=old['fullSourceUnits'].keys()
    for name,path in TESTS.items():
        text=path.read_text();relative=str(path.relative_to(ROOT))
        assert data.sha(path.read_bytes())==PINS[name]==current[relative]
        assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+\w+\s*\(',text))==COUNTS[name]
        assert 'dev.codex.schubert.nk.batch.platform.'+name not in old['suiteNames']
        assert not any(v in text for v in ['@Before','@After','@TempDir','DriverManager','ProcessBuilder','TemporaryInfrastructureException','WebStartupException','RootFailedStartRecovery','LinuxDirectoryCalls','ApiProcessLifetime','ServiceProcessResources','.install(','.retainUnknown(','Thread.sleep','Runtime.getRuntime','addShutdownHook','removeShutdownHook','RootStartupContext.create(','new RootStartupContext.NativeIo'])
    for path,pin in EXTRAS.items():assert data.sha((ROOT/path).read_bytes())==current[path]==pin
    reviewed={}
    for name,row in MAIN_UNITS.items():
        path=source_path(row);assert row['sha256']==current[path]==data.sha((ROOT/path).read_bytes());reviewed[path]=row['sha256']
        with zipfile.ZipFile(normal['jars'][row['module']]['path']) as jar:assert {n[:-6] for n in jar.namelist() if n==name+'.class' or n.startswith(name+'$') and n.endswith('.class')}==set(CLOSURES[name])
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12 and data.sha(REPORTER.read_bytes())=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    verify(invocation);PLAN.mkdir();data.write(PLAN/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewKind='FRESH_WHOLE_SOURCE_AND_ORIGINAL_TEST_REVIEW',reviewedMainInputs=reviewed,reviewedWholeTestInputs={str(p.relative_to(ROOT)):PINS[n] for n,p in TESTS.items()},currentNormalManifestSha256=COMPILE_SHA,originalWholeSuites=COUNTS,rootMemoryPortsOnly=False,memoryJournalQueryPortsOnly=True,publicDigestOnly=True,cryptoOrKeyOperationsInvoked=True,reviewedOriginalHelperInputs=EXTRAS,syntheticRetirementCallbacksInvoked=True,declaredOwnedBenignChildCount=0,declaredOwnedMonitorWorkerCount=0,declaredOwnPlatformThreadCount=1,declaredMaximumVirtualDrainWorkerCount=11,actualVirtualDrainWorkerCount=None,ownVirtualDrainWorkersInvoked=True,testOwnJavaMonotonicClockRead=True,actualRootMemoryFixtureOnly=False,actualRootNativeObservations=0,actualGetentOrSystemctlInvoked=False,actualProcRead=False,priorProductResultsTransferred=False,productTestsExecutedByThisPlan=0,newAccepted=0,formalUpdated=False))
    run.SOURCE,run.COMPILE,run.COMPILE_SHA=SOURCE,COMPILE,COMPILE_SHA
    run.SLOT=run.host.W/'pg17088-broker-cycle-query-eleven-pt-v1';run.OUT=data.BASE/'PG17088-broker-cycle-query-eleven-pt-v1'
    run.HELPER=ROOT/'tools/quality/architecture/BrokerCycleQueryElevenCurrentJunitLauncher.java'
    run.NEW_TEST=TESTS['MorningBrokerUnitCycleTest'];run.TEST_ROOT=run.NEW_TEST.parent;run.TEST_SOURCE_OVERRIDES={}
    run.EXTRA_TEST_SOURCES=(REPORTER,*(ROOT/p for p in EXTRAS));run.FIXTURES={};run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    run.step=environmental_step;run.main()
