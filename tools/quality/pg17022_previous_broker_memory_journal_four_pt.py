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
NAME=PREFIX+'MorningPreviousBroker'
MAIN_UNITS={PREFIX+n:dict(module='batch',name=PREFIX+n,sha256=h) for n,h in [('MorningPreviousBroker','6d93d8d06aef73476b0cae74fd1edbeaf73c5bdd133ae05b872089044c996629'),('BrokerJournalEvidence','18f067e88b43658b276d06a0ef889adde32d039a50e2b1ba8dd654488d2d70bb')]}
CLOSURES={NAME:[NAME+s for s in ['','$Closed','$Evidence','$NoPrior','$Query']],PREFIX+'BrokerJournalEvidence':[PREFIX+'BrokerJournalEvidence'+s for s in ['','$Anchor','$Summary']]}
METADATA={NAME+'$Evidence',NAME+'$Query'}
METADATA_FLAGS={n:1537 if n.endswith('$Evidence') else 1536 for n in METADATA}
GENERATED_METADATA=set()
COUNTS={'MorningPreviousBrokerTest':4}
PINS={'MorningPreviousBrokerTest':'893dab081db5bbb10fd45d70329df92f29496f885dfa86a69661f3aa7b970823'}
ROOT=data.ROOT
TESTS={n:ROOT/('src/schubert-nk-batch/src/test/java/'+PREFIX+n+'.java') for n in COUNTS}
EXTRAS={'src/schubert-nk-batch/src/test/java/'+PREFIX+n+'.java':h for n,h in [('BrokerJournalEvidenceTest','73ec7a8bca1a6540dec83520b7072b56fd7c988e55d9d1a86afb67b0a9125a02'),('MorningBrokerUnitCycleTest','298e637df1d718f5a04aff184bdc26cc21b9038b314b318e2fda8658d5eb3eb0'),('InspectorUnitProbeFixture','75b62aea8f3e4fbc558ec24698c7ff7d1faf4f477f34addb17e5e58f1283da2b'),('InspectorUnitSnapshotTest','edf0ce67d649d340e2e61907cc8228cd9c44fe08a21a9f011d81cdcbef4d1a63')]}
FIXTURES={}
SESSION='PG17022-PREVIOUS-BROKER-MEMORY-JOURNAL-ORIGINAL4'
REPORTER=ROOT/'tools/quality/architecture/SharedSelectedJunitReporterV1.java'
PLAN=data.BASE/'PG17021-previous-broker-memory-journal-review-v1'
def source_path(row):return 'src/schubert-nk-'+row['module']+'/src/main/java/'+row['name']+'.java'
if __name__=='__main__':
    invocation=capture(__file__);assert not PLAN.exists()
    normal=data.read_checked(COMPILE/'manifest.safe.json',COMPILE_SHA);current=normal['begin']['inputHashes']
    assert normal['source']==SOURCE and normal['actualExit']==normal['testsExecuted']==0
    old=data.read_checked(data.BASE/'PG17012-current2531-inspector-static-environment-registry-v1/manifest.json','c9545527a3a6663fd7488e7da0241e3e74c23474ae88a7b38e6a84ddc5138c51')
    assert old['source']==SOURCE and set(MAIN_UNITS)-old['fullSourceUnits'].keys()=={NAME}
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
    verify(invocation);PLAN.mkdir();data.write(PLAN/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,reviewKind='FRESH_WHOLE_SOURCE_AND_ORIGINAL_TEST_REVIEW',reviewedMainInputs=reviewed,reviewedWholeTestInputs={str(p.relative_to(ROOT)):PINS[n] for n,p in TESTS.items()},currentNormalManifestSha256=COMPILE_SHA,originalWholeSuites=COUNTS,rootMemoryPortsOnly=False,memoryJournalQueryPortsOnly=True,publicDigestOnly=True,cryptoOrKeyOperationsInvoked=True,reviewedOriginalHelperInputs=EXTRAS,syntheticRetirementCallbacksInvoked=False,declaredOwnedBenignChildCount=0,declaredOwnedMonitorWorkerCount=0,actualRootMemoryFixtureOnly=False,actualRootNativeObservations=0,actualGetentOrSystemctlInvoked=False,actualProcRead=False,priorProductResultsTransferred=False,productTestsExecutedByThisPlan=0,newAccepted=0,formalUpdated=False))
    run.SOURCE,run.COMPILE,run.COMPILE_SHA=SOURCE,COMPILE,COMPILE_SHA
    run.SLOT=run.host.W/'pg17022-previous-broker-memory-journal-four-pt-v1';run.OUT=data.BASE/'PG17022-previous-broker-memory-journal-four-pt-v1'
    run.HELPER=ROOT/'tools/quality/architecture/PreviousBrokerMemoryJournalFourCurrentJunitLauncher.java'
    run.NEW_TEST=TESTS['MorningPreviousBrokerTest'];run.TEST_ROOT=run.NEW_TEST.parent;run.TEST_SOURCE_OVERRIDES={}
    run.EXTRA_TEST_SOURCES=(REPORTER,*(ROOT/p for p in EXTRAS));run.FIXTURES={};run.COUNTS=COUNTS;run.SESSION_ID=SESSION
    run.step=environmental_step;run.main()
