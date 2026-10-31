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
NAME=PREFIX+'MorningBrokerUnitCycle'
MAIN_UNITS={PREFIX+n:dict(module='batch',name=PREFIX+n,sha256=h) for n,h in [('MorningBrokerUnitCycle','5c69b77ddb52446e8fc833222d8402da87e23ae589b8c0cdc90c6a8061c649c5'),('MorningPreviousBroker','6d93d8d06aef73476b0cae74fd1edbeaf73c5bdd133ae05b872089044c996629')]}
CLOSURES={NAME:[NAME+s for s in ['','$Live','$Baseline','$Readiness','$1','$Retain','$Observation','$Start','$Projection','$ParentProof']],PREFIX+'MorningPreviousBroker':[PREFIX+'MorningPreviousBroker'+s for s in ['','$Closed','$Evidence','$NoPrior','$Query']]}
METADATA={NAME+s for s in ['$Readiness','$Retain','$Start','$Projection','$ParentProof']}|{PREFIX+'MorningPreviousBroker'+s for s in ['$Evidence','$Query']}
METADATA_FLAGS={n:1537 if n.endswith(('$Evidence','$Readiness','$ParentProof')) else 1536 for n in METADATA}
GENERATED_METADATA=set()
COUNTS={'MorningNoPriorBrokerTest':8}
PINS={'MorningNoPriorBrokerTest':'cd5e331001d88bd146afad2f1d76b74eb21ad64a36edb72dcc3cbbaef7bf4b88'}
ROOT=data.ROOT
TESTS={n:ROOT/('src/schubert-nk-batch/src/test/java/'+PREFIX+n+'.java') for n in COUNTS}
EXTRAS={'src/schubert-nk-batch/src/test/java/'+PREFIX+n+'.java':h for n,h in {"MorningPreviousBrokerTest":"893dab081db5bbb10fd45d70329df92f29496f885dfa86a69661f3aa7b970823","BrokerJournalEvidenceTest":"73ec7a8bca1a6540dec83520b7072b56fd7c988e55d9d1a86afb67b0a9125a02","MorningBrokerUnitCycleTest":"298e637df1d718f5a04aff184bdc26cc21b9038b314b318e2fda8658d5eb3eb0","MorningStopEvidenceTest":"28f1bfc36608177e1dfce5f7664ae5df1d97a32f26eac3d7ec85ae3c79049351","RootStartupContextTest":"f3de04b3c6043aed5e6871bc1de15b8108da8cf7adacad206d0a8a0b88a71811","MaintenanceUnitTerminationTest":"458e93febbe7700c7f84034573a2464fcbb52edc929fe6826cfdc72c618d0ced","BackupUnitTerminationTest":"077c29d1aad07c974ba31aa621278a0c8589359363b3f9ea526e0efc3b4702ea","InspectorUnitProbeFixture":"75b62aea8f3e4fbc558ec24698c7ff7d1faf4f477f34addb17e5e58f1283da2b","InspectorUnitSnapshotTest":"edf0ce67d649d340e2e61907cc8228cd9c44fe08a21a9f011d81cdcbef4d1a63"}.items()}
FIXTURES={'src/schubert-nk-batch/src/test/resources/ops/issuer-stop-present-no-prior-golden.txt':'5caea92ed7cff7b6d70dfbcc89dd5b5464c454b5eddfc8c9011f398cb5be60b9','src/schubert-nk-batch/src/test/resources/ops/issuer-stop-absent-no-prior-golden.txt':'f3995ad5093646bc47f6d8f2bcd1dc4a03fe527bc03aa5262b5c0bd7c17d1148'}
SESSION='PG17054-NO-PRIOR-BROKER-MEMORY-ORIGINAL8'
REPORTER=ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
PLAN=data.BASE/'PG17053-no-prior-broker-memory-review-v1'
def source_path(row):return 'src/schubert-nk-'+row['module']+'/src/main/java/'+row['name']+'.java'
if __name__=='__main__':
    invocation=capture(__file__);assert not PLAN.exists()
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA);current=normal['begin']['inputHashes']
    assert normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0
    old=data.read_checked(data.BASE/'PG17044-current2539-inspector-run-environment-registry-v1/manifest.json','294c86adb70497b9b38a630721c587e8ac015f0c3c31f49de000c729ca1740fe')
    assert old['source']==SOURCE and set(MAIN_UNITS)-old['fullSourceUnits'].keys()=={NAME}
    for name,path in TESTS.items():
        text=path.read_text();relative=str(path.relative_to(ROOT))
        assert data.sha(path.read_bytes())==PINS[name]==current[relative]
        assert text.count('@Test')==len(re.findall(r'@Test\s+void\s+\w+\s*\(',text))==COUNTS[name]
        assert 'dev.codex.schubert.nk.batch.platform.'+name not in old['suiteNames']
        assert not any(v in text for v in ['@Before','@After','@TempDir','DriverManager','ProcessBuilder','TemporaryInfrastructureException','WebStartupException','RootFailedStartRecovery','LinuxDirectoryCalls','ApiProcessLifetime','ServiceProcessResources','.install(','.retainUnknown(','Thread.sleep','Runtime.getRuntime','addShutdownHook','removeShutdownHook','RootStartupContext.create(','new RootStartupContext.NativeIo'])
    for path,pin in {**EXTRAS,**FIXTURES}.items():assert data.sha((ROOT/path).read_bytes())==current[path]==pin
    reviewed={}
    for name,row in MAIN_UNITS.items():
        path=source_path(row);assert row['sha256']==current[path]==data.sha((ROOT/path).read_bytes());reviewed[path]=row['sha256']
        with zipfile.ZipFile(normal['jars'][row['module']]['path']) as jar:assert {n[:-6] for n in jar.namelist() if n==name+'.class' or n.startswith(name+'$') and n.endswith('.class')}==set(CLOSURES[name])
    proof=data.read_checked(data.BASE/'PG13728-shared-reporter-selftest-post-v1/manifest.json','32b4a366c2dd35ee78e779342de1ae22a3c52dd4dbd6c72d36c691d75886ea3c')
    assert proof['actualExit']==proof['productTestsExecuted']==0 and proof['toolChecksIndependentlyConfirmed']==12 and data.sha(REPORTER.read_bytes())=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
    verify(invocation);PLAN.mkdir();data.write(PLAN/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewKind='FRESH_WHOLE_SOURCE_AND_ORIGINAL_TEST_REVIEW',reviewedMainInputs=reviewed,reviewedWholeTestInputs={str(p.relative_to(ROOT)):PINS[n] for n,p in TESTS.items()},currentNormalManifestSha256=COMPILE_SHA,originalWholeSuites=COUNTS,rootMemoryPortsOnly=True,memoryJournalQueryPortsOnly=True,publicDigestOnly=True,cryptoOrKeyOperationsInvoked=True,reviewedOriginalHelperInputs=EXTRAS,syntheticRetirementCallbacksInvoked=True,declaredOwnedBenignChildCount=0,declaredOwnedMonitorWorkerCount=0,actualRootMemoryFixtureOnly=True,actualRootNativeObservations=0,actualGetentOrSystemctlInvoked=False,actualProcRead=False,priorProductResultsTransferred=False,declaredOwnThreadCount=2,testPublicGoldenResourcesRead=True,productTestsExecutedByThisPlan=0,newAccepted=0,formalUpdated=False))
    run.SOURCE,run.COMPILE,run.COMPILE_SHA=SOURCE,COMPILE,COMPILE_SHA
    run.SLOT=run.host.W/'pg17054-no-prior-broker-memory-eight-pt-v1';run.OUT=data.BASE/'PG17054-no-prior-broker-memory-eight-pt-v1'
    run.HELPER=ROOT/'tools/quality/architecture/NoPriorBrokerMemoryEightCurrentJunitLauncher.java'
    run.NEW_TEST=TESTS['MorningNoPriorBrokerTest'];run.TEST_ROOT=run.NEW_TEST.parent;run.TEST_SOURCE_OVERRIDES={}
    run.EXTRA_TEST_SOURCES=(REPORTER,*(ROOT/p for p in EXTRAS));run.FIXTURES=FIXTURES;run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    run.step=environmental_step;run.main()
